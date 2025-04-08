# backend/api/controllers/results.py
"""
Results controller for Derby Director
"""

from datetime import datetime
from typing import Annotated, List, Optional, Dict, AsyncGenerator, Any

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from litestar import get, post, put, delete
from litestar.controller import Controller
from litestar.di import Provide
from litestar.params import Dependency, Parameter as Query
from litestar.exceptions import NotFoundException, ClientException
from litestar.status_codes import HTTP_200_OK, HTTP_201_CREATED, HTTP_204_NO_CONTENT

from backend.api.models import Heat, Round, RacerHeat, Racer, RaceResult
from backend.api.schemas import (
    ResultCreate, ResultUpdate, ResultResponse, ResultDetail,
    HeatResultRequest, HeatResultsResponse
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


class ResultController(Controller):
    """Controller for race result endpoints"""
    
    path = "/results"
    dependencies = {"session": Provide(provide_session),
                    "user": get_jwt_user
    }
    
    @get("/", status_code=HTTP_200_OK)
    async def get_results(
        self,
        session: Annotated[AsyncSession, Dependency()],
        heat_id: Annotated[Optional[int], Query(description="Filter by heat ID")] = None,
        racer_id: Annotated[Optional[int], Query(description="Filter by racer ID")] = None,
        round_id: Annotated[Optional[int], Query(description="Filter by round ID")] = None
    ) -> List[ResultDetail]:
        """Get race results with optional filtering"""
        query = (
            select(
                RaceResult, 
                Racer.firstname, 
                Racer.lastname,
                Racer.carno,
                Heat.heat.label("heat_number"),
                Round.name.label("round_name")
            )
            .join(Racer, RaceResult.racer_id == Racer.id)
            .join(Heat, RaceResult.heat_id == Heat.id)
            .join(Round, Heat.roundid == Round.id)
        )
        
        # Apply filters
        if heat_id is not None:
            query = query.filter(RaceResult.heat_id == heat_id)
            
        if racer_id is not None:
            query = query.filter(RaceResult.racer_id == racer_id)
            
        if round_id is not None:
            query = query.filter(Heat.roundid == round_id)
            
        # Execute query
        result = await session.execute(query)
        rows = result.all()
        
        # Map to response objects
        results_list = []
        for race_result, firstname, lastname, carno, heat_number, round_name in rows:
            result_detail = ResultDetail(
                id=race_result.id,
                heat_id=race_result.heat_id,
                racer_id=race_result.racer_id,
                lane=race_result.lane,
                time=race_result.time,
                place=race_result.place,
                completed=race_result.completed,
                racer_name=f"{firstname} {lastname}",
                car_number=carno,
                heat_number=heat_number,
                round_name=round_name
            )
            results_list.append(result_detail)
        
        return results_list
    
    @get("/heat/{heat_id:int}", status_code=HTTP_200_OK)
    async def get_heat_results(
        self,
        heat_id: int,
        session: Annotated[AsyncSession, Dependency()]
    ) -> HeatResultsResponse:
        """Get all results for a specific heat"""
        # Get heat info
        heat_query = (
            select(Heat, Round.name.label("round_name"))
            .join(Round, Heat.roundid == Round.id)
            .filter(Heat.id == heat_id)
        )
        
        heat_result = await session.execute(heat_query)
        heat_row = heat_result.one_or_none()
        
        if not heat_row:
            raise NotFoundException(f"Heat with ID {heat_id} not found")
        
        heat, round_name = heat_row
        
        # Get results for this heat
        results_query = (
            select(
                RaceResult, 
                Racer.firstname, 
                Racer.lastname,
                Racer.carno
            )
            .join(Racer, RaceResult.racer_id == Racer.id)
            .filter(RaceResult.heat_id == heat_id)
            .order_by(RaceResult.lane)
        )
        
        results_rows = await session.execute(results_query)
        
        # Map to response objects
        results_list = []
        for race_result, firstname, lastname, carno in results_rows:
            result_detail = ResultDetail(
                id=race_result.id,
                heat_id=race_result.heat_id,
                racer_id=race_result.racer_id,
                lane=race_result.lane,
                time=race_result.time,
                place=race_result.place,
                completed=race_result.completed,
                racer_name=f"{firstname} {lastname}",
                car_number=carno,
                heat_number=heat.heat,
                round_name=round_name
            )
            results_list.append(result_detail)
        
        # All results are complete if the heat is marked complete
        all_completed = heat.status == "completed"
        
        return HeatResultsResponse(
            heat_id=heat_id,
            round_name=round_name,
            heat_number=heat.heat,
            results=results_list,
            completed=all_completed
        )
    
    @post("/heat", status_code=HTTP_201_CREATED)
    async def record_heat_results(
        self,
        data: HeatResultRequest,
        session: Annotated[AsyncSession, Dependency()],
        user: Annotated[dict, Dependency()]
    ) -> HeatResultsResponse:
        """Record results for a complete heat"""
        # Get heat
        heat = await session.get(Heat, data.heat_id)
        if not heat:
            raise NotFoundException(f"Heat with ID {data.heat_id} not found")
        
        # Delete any existing results for this heat
        await session.execute(
            RaceResult.__table__.delete().where(RaceResult.heat_id == data.heat_id)
        )
        
        # Create new results
        for result_data in data.results:
            # Verify the racer exists
            racer = await session.get(Racer, result_data.racer_id)
            if not racer:
                await session.rollback()
                raise NotFoundException(f"Racer with ID {result_data.racer_id} not found")
            
            # Create result
            result = RaceResult(
                heat_id=data.heat_id,
                racer_id=result_data.racer_id,
                lane=result_data.lane,
                time=result_data.time,
                place=result_data.place,
                completed=True
            )
            session.add(result)
        
        # Update heat status to completed
        heat.status = "completed"
        heat.completed_time = datetime.utcnow()
        
        await session.commit()
        
        # Return the updated heat results
        return await self.get_heat_results(data.heat_id, session)
    
    @delete("/heat/{heat_id:int}", status_code=HTTP_204_NO_CONTENT)
    async def delete_heat_results(
        self,
        heat_id: int,
        session: Annotated[AsyncSession, Dependency()],
        user: Annotated[dict, Dependency()]
    ) -> None:
        """Delete all results for a specific heat"""
        # Get heat
        heat = await session.get(Heat, heat_id)
        if not heat:
            raise NotFoundException(f"Heat with ID {heat_id} not found")
        
        # Delete results
        await session.execute(
            RaceResult.__table__.delete().where(RaceResult.heat_id == heat_id)
        )
        
        # Update heat status back to scheduled
        heat.status = "scheduled"
        heat.completed_time = None
        
        await session.commit()