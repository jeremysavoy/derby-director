# derby_director/api/controllers/rounds.py
"""
Rounds controller for Derby Director
"""

from typing import Annotated, List, Optional, Dict, AsyncGenerator, Any

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from litestar import get, post, put, delete
from litestar.controller import Controller
from litestar.di import Provide
from litestar.params import Dependency, Parameter
from litestar.exceptions import NotFoundException, ClientException
from litestar.status_codes import HTTP_200_OK, HTTP_201_CREATED, HTTP_204_NO_CONTENT

from backend.api.models import Round, Division, Heat
from backend.api.middleware.auth import get_jwt_user


async def provide_session() -> AsyncGenerator[AsyncSession, None]:
    """Dependency provider for database session"""
    from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
    from backend.config import DATABASE_URL
    
    engine = create_async_engine(DATABASE_URL)
    async_session = async_sessionmaker(engine, expire_on_commit=False)
    
    async with async_session() as session:
        yield session


# Create schema definitions for requests and responses
from pydantic import BaseModel, Field


class RoundBase(BaseModel):
    """Base schema for round data"""
    name: str = Field(..., description="Round name")
    divisionid: Optional[int] = Field(None, description="Division ID (null for all divisions)")
    roundno: int = Field(..., description="Round number (for ordering)")
    phase: str = Field("normal", description="Round phase (normal, semifinal, final, etc)")
    charttype: str = Field("roster", description="Chart type for display")


class RoundCreate(RoundBase):
    """Schema for creating a new round"""
    pass


class RoundUpdate(BaseModel):
    """Schema for updating an existing round"""
    name: Optional[str] = Field(None, description="Round name")
    divisionid: Optional[int] = Field(None, description="Division ID (null for all divisions)")
    roundno: Optional[int] = Field(None, description="Round number (for ordering)")
    phase: Optional[str] = Field(None, description="Round phase (normal, semifinal, final, etc)")
    charttype: Optional[str] = Field(None, description="Chart type for display")


class RoundResponse(RoundBase):
    """Schema for round responses"""
    id: int = Field(..., description="Round ID")
    division_name: Optional[str] = Field(None, description="Name of the division for this round")
    
    class Config:
        from_attributes = True


class RoundWithHeats(RoundResponse):
    """Schema for round with heat count information"""
    heat_count: int = Field(0, description="Number of heats in this round")
    completed_heats: int = Field(0, description="Number of completed heats")
    
    class Config:
        from_attributes = True


class RoundController(Controller):
    """Controller for round-related endpoints"""
    
    path = "/rounds"
    dependencies = {"session": Provide(provide_session),               
                    "user": Provide(get_jwt_user)
    }
    
    @get("/", status_code=HTTP_200_OK)
    async def get_rounds(
        self,
        session: AsyncSession = Dependency(),
        division_id: Optional[int] = Parameter(None, query="division_id", description="Filter by division ID")
    ) -> List[RoundWithHeats]:
        """Get all rounds with optional filtering by division"""
        # Build query to get rounds with division name
        query = (
            select(
                Round, 
                Division.name.label("division_name")
            )
            .outerjoin(Division, Round.divisionid == Division.id)
            .order_by(Round.roundno)
        )
        
        # Apply division filter if provided
        if division_id is not None:
            query = query.filter(Round.divisionid == division_id)
            
        # Execute query
        result = await session.execute(query)
        rounds_with_divisions = result.all()
        
        # Get heat counts for each round
        round_ids = [r[0].id for r in rounds_with_divisions]
        
        # Query heat counts and completed heat counts
        heat_counts = {}
        completed_counts = {}
        
        if round_ids:
            # Get total heat counts per round
            heat_count_query = (
                select(Heat.roundid, func.count(Heat.id))
                .filter(Heat.roundid.in_(round_ids))
                .group_by(Heat.roundid)
            )
            heat_count_result = await session.execute(heat_count_query)
            heat_counts = dict(heat_count_result.all())
            
            # Get completed heat counts per round
            completed_count_query = (
                select(Heat.roundid, func.count(Heat.id))
                .filter(Heat.roundid.in_(round_ids), Heat.status == "completed")
                .group_by(Heat.roundid)
            )
            completed_count_result = await session.execute(completed_count_query)
            completed_counts = dict(completed_count_result.all())
        
        # Assemble responses with heat counts
        responses = []
        for round_obj, division_name in rounds_with_divisions:
            # Create the response model
            round_response = RoundWithHeats(
                id=round_obj.id,
                name=round_obj.name,
                divisionid=round_obj.divisionid,
                roundno=round_obj.roundno,
                phase=round_obj.phase,
                charttype=round_obj.charttype,
                division_name=division_name,
                heat_count=heat_counts.get(round_obj.id, 0),
                completed_heats=completed_counts.get(round_obj.id, 0)
            )
            responses.append(round_response)
        
        return responses
    
    @get("/{round_id:int}", status_code=HTTP_200_OK)
    async def get_round(
        self,
        round_id: int,
        session: AsyncSession = Dependency()
    ) -> RoundWithHeats:
        """Get a single round by ID with division and heat information"""
        query = (
            select(Round, Division.name.label("division_name"))
            .outerjoin(Division, Round.divisionid == Division.id)
            .filter(Round.id == round_id)
        )
        
        result = await session.execute(query)
        round_data = result.one_or_none()
        
        if not round_data:
            raise NotFoundException(f"Round with ID {round_id} not found")
        
        round_obj, division_name = round_data
        
        # Get heat counts for this round
        heat_count_query = select(func.count()).select_from(Heat).filter(Heat.roundid == round_id)
        heat_count = await session.execute(heat_count_query)
        total_heats = heat_count.scalar() or 0
        
        # Get completed heat count
        completed_count_query = (
            select(func.count())
            .select_from(Heat)
            .filter(Heat.roundid == round_id, Heat.status == "completed")
        )
        completed_count = await session.execute(completed_count_query)
        completed_heats = completed_count.scalar() or 0
        
        # Create response
        return RoundWithHeats(
            id=round_obj.id,
            name=round_obj.name,
            divisionid=round_obj.divisionid,
            roundno=round_obj.roundno,
            phase=round_obj.phase,
            charttype=round_obj.charttype,
            division_name=division_name,
            heat_count=total_heats,
            completed_heats=completed_heats
        )
    
    @post("/", status_code=HTTP_201_CREATED)
    async def create_round(
        self,
        data: RoundCreate,
        session: AsyncSession = Dependency(),
        user: dict = Dependency()
    ) -> RoundResponse:
        """Create a new round"""
        # Verify division exists if provided
        if data.divisionid is not None:
            division_obj = await session.get(Division, data.divisionid)
            if not division_obj:
                raise NotFoundException(f"Division with ID {data.divisionid} not found")
        
        # Create round
        round_obj = Round(**data.model_dump())
        session.add(round_obj)
        await session.commit()
        await session.refresh(round_obj)
        
        # Get division name for response if applicable
        division_name = None
        if round_obj.divisionid:
            division_query = select(Division.name).filter(Division.id == round_obj.divisionid)
            division_result = await session.execute(division_query)
            division_name = division_result.scalar_one_or_none()
        
        # Create response
        return RoundResponse(
            id=round_obj.id,
            name=round_obj.name,
            divisionid=round_obj.divisionid,
            roundno=round_obj.roundno,
            phase=round_obj.phase,
            charttype=round_obj.charttype,
            division_name=division_name
        )
    
    @put("/{round_id:int}", status_code=HTTP_200_OK)
    async def update_round(
        self,
        round_id: int,
        data: RoundUpdate,
        session: AsyncSession = Dependency(),
        user: dict = Dependency()
    ) -> RoundResponse:
        """Update an existing round"""
        # Get round
        round_obj = await session.get(Round, round_id)
        if not round_obj:
            raise NotFoundException(f"Round with ID {round_id} not found")
        
        # Verify division exists if changing division
        if data.divisionid is not None and data.divisionid != round_obj.divisionid:
            if data.divisionid:  # Only check if not setting to None
                division_obj = await session.get(Division, data.divisionid)
                if not division_obj:
                    raise NotFoundException(f"Division with ID {data.divisionid} not found")
        
        # Update fields
        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(round_obj, key, value)
        
        # Save changes
        await session.commit()
        await session.refresh(round_obj)
        
        # Get division name for response if applicable
        division_name = None
        if round_obj.divisionid:
            division_query = select(Division.name).filter(Division.id == round_obj.divisionid)
            division_result = await session.execute(division_query)
            division_name = division_result.scalar_one_or_none()
        
        # Create response
        return RoundResponse(
            id=round_obj.id,
            name=round_obj.name,
            divisionid=round_obj.divisionid,
            roundno=round_obj.roundno,
            phase=round_obj.phase,
            charttype=round_obj.charttype,
            division_name=division_name
        )
    
    @delete("/{round_id:int}", status_code=HTTP_204_NO_CONTENT)
    async def delete_round(
        self,
        round_id: int,
        session: AsyncSession = Dependency(),
        user: dict = Dependency()
    ) -> None:
        """Delete a round"""
        # Get round
        round_obj = await session.get(Round, round_id)
        if not round_obj:
            raise NotFoundException(f"Round with ID {round_id} not found")
        
        # Check if round has heats
        heat_count_query = select(func.count()).select_from(Heat).filter(Heat.roundid == round_id)
        heat_count = await session.execute(heat_count_query)
        total_heats = heat_count.scalar() or 0
        
        if total_heats > 0:
            # Can't delete a round with heats
            raise ClientException(
                f"Cannot delete round with {total_heats} heats. "
                "Delete the heats first or reassign them to another round."
            )
        
        # Delete round
        await session.delete(round_obj)
        await session.commit()
    
    @get("/{round_id:int}/heats", status_code=HTTP_200_OK)
    async def get_round_heats(
        self,
        round_id: int,
        session: AsyncSession = Dependency()
    ) -> Dict[str, Any]:
        """Get all heats for a specific round"""
        # Check if round exists
        round_obj = await session.get(Round, round_id)
        if not round_obj:
            raise NotFoundException(f"Round with ID {round_id} not found")
        
        # Reuse the existing heat controller to get heats for this round
        from backend.api.controllers.heats import HeatController
        heat_controller = HeatController()
        
        # Call the get_heats method filtering by round_id
        heats = await heat_controller.get_heats(session=session, round_id=round_id)
        
        # Return with round info and heats
        return {
            "round": {
                "id": round_obj.id,
                "name": round_obj.name,
                "phase": round_obj.phase
            },
            "heats": heats
        }