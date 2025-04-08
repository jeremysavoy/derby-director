# backend/api/controllers/heats.py
"""
Heats controller for Derby Director
"""

from datetime import datetime
from typing import Annotated, List, Optional, Dict, AsyncGenerator, Any

from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from litestar import get, post, put, delete
from litestar.controller import Controller
from litestar.di import Provide
from litestar.params import Dependency, Parameter as Query
from litestar.exceptions import NotFoundException, ClientException
from litestar.status_codes import HTTP_200_OK, HTTP_201_CREATED, HTTP_204_NO_CONTENT

from backend.api.models import Heat, Round, RacerHeat, Racer
from backend.api.schemas import (
    HeatCreate, HeatUpdate, HeatResponse, HeatDetail,
    LaneAssignmentResponse, LaneAssignment
)
from backend.api.middleware.auth import get_jwt_user


async def provide_session() -> AsyncGenerator[AsyncSession, None]:
    """Dependency provider for database session"""
    from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
    from backend.config import DATABASE_URL
    
    engine = create_async_engine(DATABASE_URL)
    async_session = async_sessionmaker(engine, expire_on_commit=False)
    
    async with async_session() as session:
        yield session


class HeatController(Controller):
    """Controller for heat-related endpoints"""
    
    path = "/heats"
    dependencies = {"session": Provide(provide_session),
                    "user": get_jwt_user
    }
    
    @get("/", status_code=HTTP_200_OK)
    async def get_heats(
        self,
        session: Annotated[AsyncSession, Dependency()],
        round_id: Annotated[Optional[int], Query(description="Filter by round ID")] = None,
        status: Annotated[Optional[str], Query(description="Filter by status")] = None,
        upcoming: Annotated[Optional[bool], Query(description="Get only upcoming heats")] = False
    ) -> List[HeatResponse]:
        """Get all heats with optional filtering"""
        query = select(Heat)
        
        # Apply filters
        if round_id is not None:
            query = query.filter(Heat.roundid == round_id)
            
        if status is not None:
            query = query.filter(Heat.status == status)
            
        if upcoming:
            query = query.filter(or_(
                Heat.status == "scheduled",
                Heat.status == "in_progress"
            ))
        
        # Order by round and heat number
        query = query.order_by(Heat.roundid, Heat.heat)
        
        # Execute query
        result = await session.execute(query)
        heats = result.scalars().all()
        
        return [HeatResponse.model_validate(heat) for heat in heats]
    
    @get("/{heat_id:int}", status_code=HTTP_200_OK)
    async def get_heat(
        self,
        heat_id: int,
        session: Annotated[AsyncSession, Dependency()]
    ) -> HeatDetail:
        """Get a single heat by ID with lane assignments"""
        # Get heat with round info
        query = (
            select(Heat, Round.name.label("round_name"))
            .join(Round, Heat.roundid == Round.id)
            .filter(Heat.id == heat_id)
        )
        
        result = await session.execute(query)
        row = result.one_or_none()
        
        if not row:
            raise NotFoundException(f"Heat with ID {heat_id} not found")
        
        heat, round_name = row
        
        # Get lane assignments with racer info
        lanes_query = (
            select(
                RacerHeat.lane,
                RacerHeat.racer_id,
                Racer.firstname,
                Racer.lastname,
                Racer.carno
            )
            .join(Racer, RacerHeat.racer_id == Racer.id)
            .filter(RacerHeat.heat_id == heat_id)
            .order_by(RacerHeat.lane)
        )
        
        lanes_result = await session.execute(lanes_query)
        lanes = [
            LaneAssignmentResponse(
                lane=lane,
                racer_id=racer_id,
                racer_name=f"{firstname} {lastname}",
                car_number=carno
            )
            for lane, racer_id, firstname, lastname, carno in lanes_result
        ]
        
        # Create response
        response = HeatDetail.model_validate(heat)
        response.lanes = lanes
        response.round_name = round_name
        
        return response
    
    @post("/", status_code=HTTP_201_CREATED)
    async def create_heat(
        self,
        data: HeatCreate,
        session: Annotated[AsyncSession, Dependency()],
        user: Annotated[dict, Dependency()]
    ) -> HeatDetail:
        """Create a new heat with lane assignments"""
        # Verify round exists
        round_obj = await session.get(Round, data.roundid)
        if not round_obj:
            raise NotFoundException(f"Round with ID {data.roundid} not found")
        
        # Create heat
        heat = Heat(
            roundid=data.roundid,
            heat=data.heat,
            status="scheduled"
        )
        
        session.add(heat)
        await session.flush()  # Get the heat ID
        
        # Create lane assignments
        for lane_data in data.lanes:
            # Verify racer exists
            racer = await session.get(Racer, lane_data.racer_id)
            if not racer:
                await session.rollback()
                raise NotFoundException(f"Racer with ID {lane_data.racer_id} not found")
            
            # Create lane assignment
            lane = RacerHeat(
                heat_id=heat.id,
                lane=lane_data.lane,
                racer_id=lane_data.racer_id
            )
            session.add(lane)
        
        await session.commit()
        await session.refresh(heat)
        
        # Return the created heat with details
        return await self.get_heat(heat.id, session)
    
    @put("/{heat_id:int}", status_code=HTTP_200_OK)
    async def update_heat(
        self,
        heat_id: int,
        data: HeatUpdate,
        session: Annotated[AsyncSession, Dependency()],
        user: Annotated[dict, Dependency()]
    ) -> HeatDetail:
        """Update an existing heat"""
        # Get heat
        heat = await session.get(Heat, heat_id)
        if not heat:
            raise NotFoundException(f"Heat with ID {heat_id} not found")
        
        # Update status if provided
        if data.status is not None:
            heat.status = data.status
            
            # Set completed time if status is "completed"
            if data.status == "completed" and not heat.completed_time:
                heat.completed_time = datetime.utcnow()
        
        # Update lane assignments if provided
        if data.lanes is not None:
            # Delete existing lane assignments
            await session.execute(
                RacerHeat.__table__.delete().where(RacerHeat.heat_id == heat_id)
            )
            
            # Create new lane assignments
            for lane_data in data.lanes:
                # Verify racer exists
                racer = await session.get(Racer, lane_data.racer_id)
                if not racer:
                    await session.rollback()
                    raise NotFoundException(f"Racer with ID {lane_data.racer_id} not found")
                
                # Create lane assignment
                lane = RacerHeat(
                    heat_id=heat_id,
                    lane=lane_data.lane,
                    racer_id=lane_data.racer_id
                )
                session.add(lane)
        
        await session.commit()
        await session.refresh(heat)
        
        # Return the updated heat with details
        return await self.get_heat(heat_id, session)
    
    @delete("/{heat_id:int}", status_code=HTTP_204_NO_CONTENT)
    async def delete_heat(
        self,
        heat_id: int,
        session: Annotated[AsyncSession, Dependency()],
        user: Annotated[dict, Dependency()]
    ) -> None:
        """Delete a heat"""
        # Get heat
        heat = await session.get(Heat, heat_id)
        if not heat:
            raise NotFoundException(f"Heat with ID {heat_id} not found")
        
        # Don't allow deletion of completed heats with results
        if heat.status == "completed":
            # Check if heat has results
            query = select(func.count()).select_from(Heat).where(Heat.id == heat_id)
            result = await session.execute(query)
            count = result.scalar()
            
            if count > 0:
                raise ClientException(
                    "Cannot delete a completed heat with results. "
                    "Delete the results first or change the heat status."
                )
        
        # Delete lane assignments
        await session.execute(
            RacerHeat.__table__.delete().where(RacerHeat.heat_id == heat_id)
        )
        
        # Delete heat
        await session.delete(heat)
        await session.commit()