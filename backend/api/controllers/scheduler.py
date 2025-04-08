# backend/api/controllers/scheduler.py
"""
Race scheduler controller for Derby Director
Provides endpoints to create rounds, generate heats, and manage race schedules
"""

from typing import Annotated, List, Dict, Optional, AsyncGenerator, Any

from sqlalchemy.ext.asyncio import AsyncSession
from litestar import get, post, Controller
from litestar.di import Provide
from litestar.params import Dependency, Parameter
from litestar.exceptions import HTTPException
from litestar.status_codes import HTTP_200_OK, HTTP_201_CREATED

from backend.api.services import RaceScheduler
from backend.api.models import Round, Heat
from backend.api.middleware.auth import get_jwt_user


async def provide_session() -> AsyncGenerator[AsyncSession, None]:
    """Dependency provider for database session"""
    from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
    from backend.config import DATABASE_URL
    
    engine = create_async_engine(DATABASE_URL)
    async_session = async_sessionmaker(engine, expire_on_commit=False)
    
    async with async_session() as session:
        yield session


# Define schemas for the scheduler API
from pydantic import BaseModel, Field


class CreatePreliminaryRoundRequest(BaseModel):
    """Request to create a preliminary round"""
    division_id: int = Field(..., description="Division ID to create round for")
    name: Optional[str] = Field(None, description="Optional round name")


class CreateFinalRoundRequest(BaseModel):
    """Request to create a final round"""
    division_id: int = Field(..., description="Division ID to create round for")
    name: Optional[str] = Field(None, description="Optional round name")


class CreateChampionshipRoundRequest(BaseModel):
    """Request to create a championship round"""
    name: Optional[str] = Field("Championship Finals", description="Optional round name")


class GenerateHeatsRequest(BaseModel):
    """Request to generate heats for a round"""
    round_id: int = Field(..., description="Round ID to generate heats for")
    lanes_per_heat: int = Field(4, description="Number of lanes on the track")


class AdvanceRacersRequest(BaseModel):
    """Request to advance racers from preliminary to final round"""
    preliminary_round_id: int = Field(..., description="Preliminary round ID")
    final_round_id: int = Field(..., description="Final round ID")
    top_count: int = Field(4, description="Number of top racers to advance")


class RoundResponse(BaseModel):
    """Response containing round information"""
    id: int = Field(..., description="Round ID")
    name: str = Field(..., description="Round name")
    divisionid: Optional[int] = Field(None, description="Division ID (may be None for championship)")
    roundno: int = Field(..., description="Round number")
    phase: str = Field(..., description="Round phase")
    charttype: str = Field(..., description="Chart type")


class HeatResponse(BaseModel):
    """Response containing heat information"""
    id: int = Field(..., description="Heat ID")
    round_id: int = Field(..., description="Round ID")
    heat: int = Field(..., description="Heat number")
    status: str = Field(..., description="Heat status")


class HeatsGeneratedResponse(BaseModel):
    """Response after generating heats"""
    round_id: int = Field(..., description="Round ID")
    round_name: str = Field(..., description="Round name")
    heats_created: int = Field(..., description="Number of heats created")
    heats: List[HeatResponse] = Field(..., description="List of created heats")


class RacerStanding(BaseModel):
    """Schema for racer standings"""
    racer_id: int = Field(..., description="Racer ID")
    name: str = Field(..., description="Racer name")
    car_number: Optional[str] = Field(None, description="Car number")
    divisionid: int = Field(..., description="Division ID")
    division_name: str = Field(..., description="Division name")
    avg_time: Optional[float] = Field(None, description="Average race time")
    best_time: Optional[float] = Field(None, description="Best race time")
    race_count: int = Field(..., description="Number of races completed")


class SchedulerController(Controller):
    """Controller for race scheduling operations"""
    
    path = "/scheduler"
    dependencies = {"session": Provide(provide_session),
                    "user": Dependency(get_jwt_user)
    }
    
    @post("/rounds/preliminary", status_code=HTTP_201_CREATED)
    async def create_preliminary_round(
        self,
        data: CreatePreliminaryRoundRequest,
        session: AsyncSession = Dependency(),
        user: dict = Dependency()
    ) -> RoundResponse:
        """Create a preliminary round for a division"""
        try:
            scheduler = RaceScheduler(session)
            round_obj = await scheduler.create_preliminary_round(
                division_id=data.division_id,
                name=data.name
            )
            
            return RoundResponse(
                id=round_obj.id,
                name=round_obj.name,
                divisionid=round_obj.divisionid,
                roundno=round_obj.roundno,
                phase=round_obj.phase,
                charttype=round_obj.charttype
            )
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to create preliminary round: {str(e)}")
    
    @post("/rounds/final", status_code=HTTP_201_CREATED)
    async def create_final_round(
        self,
        data: CreateFinalRoundRequest,
        session: AsyncSession = Dependency(),
        user: dict = Dependency()
    ) -> RoundResponse:
        """Create a final round for a division"""
        try:
            scheduler = RaceScheduler(session)
            round_obj = await scheduler.create_final_round(
                division_id=data.division_id,
                name=data.name
            )
            
            return RoundResponse(
                id=round_obj.id,
                name=round_obj.name,
                divisionid=round_obj.divisionid,
                roundno=round_obj.roundno,
                phase=round_obj.phase,
                charttype=round_obj.charttype
            )
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to create final round: {str(e)}")
    
    @post("/rounds/championship", status_code=HTTP_201_CREATED)
    async def create_championship_round(
        self,
        data: CreateChampionshipRoundRequest,
        session: AsyncSession = Dependency(),
        user: dict = Dependency()
    ) -> RoundResponse:
        """Create a championship round for top racers across all divisions"""
        try:
            scheduler = RaceScheduler(session)
            round_obj = await scheduler.create_championship_round(
                name=data.name
            )
            
            return RoundResponse(
                id=round_obj.id,
                name=round_obj.name,
                divisionid=round_obj.divisionid,
                roundno=round_obj.roundno,
                phase=round_obj.phase,
                charttype=round_obj.charttype
            )
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to create championship round: {str(e)}")
    
    @post("/heats/generate", status_code=HTTP_201_CREATED)
    async def generate_heats(
        self,
        data: GenerateHeatsRequest,
        session: AsyncSession = Dependency(),
        user: dict = Dependency()
    ) -> HeatsGeneratedResponse:
        """Generate heats for a round based on its type"""
        try:
            scheduler = RaceScheduler(session)
            heats = await scheduler.generate_heats_for_round(
                round_id=data.round_id,
                lanes_per_heat=data.lanes_per_heat
            )
            
            # Get round info for response
            round_obj = await session.get(Round, data.round_id)
            
            # Create response
            heat_responses = [
                HeatResponse(
                    id=heat.id,
                    round_id=heat.roundid,
                    heat=heat.heat,
                    status=heat.status
                )
                for heat in heats
            ]
            
            return HeatsGeneratedResponse(
                round_id=data.round_id,
                round_name=round_obj.name,
                heats_created=len(heats),
                heats=heat_responses
            )
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to generate heats: {str(e)}")
    
    @post("/advance", status_code=HTTP_201_CREATED)
    async def advance_racers(
        self,
        data: AdvanceRacersRequest,
        session: AsyncSession = Dependency(),
        user: dict = Dependency()
    ) -> HeatsGeneratedResponse:
        """Advance top racers from preliminary to final round"""
        try:
            scheduler = RaceScheduler(session)
            heats = await scheduler.advance_racers_to_finals(
                preliminary_round_id=data.preliminary_round_id,
                final_round_id=data.final_round_id,
                top_count=data.top_count
            )
            
            # Get round info for response
            round_obj = await session.get(Round, data.final_round_id)
            
            # Create response
            heat_responses = [
                HeatResponse(
                    id=heat.id,
                    round_id=heat.roundid,
                    heat=heat.heat,
                    status=heat.status
                )
                for heat in heats
            ]
            
            return HeatsGeneratedResponse(
                round_id=data.final_round_id,
                round_name=round_obj.name,
                heats_created=len(heats),
                heats=heat_responses
            )
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to advance racers: {str(e)}")
    
    @post("/championship/heats", status_code=HTTP_201_CREATED)
    async def create_championship_heats(
        self,
        data: GenerateHeatsRequest,
        session: AsyncSession = Dependency(),
        user: dict = Dependency()
    ) -> HeatsGeneratedResponse:
        """Create championship heats with division winners"""
        try:
            scheduler = RaceScheduler(session)
            heats = await scheduler.create_championship_heats(
                round_id=data.round_id,
                lanes_per_heat=data.lanes_per_heat
            )
            
            # Get round info for response
            round_obj = await session.get(Round, data.round_id)
            
            # Create response
            heat_responses = [
                HeatResponse(
                    id=heat.id,
                    round_id=heat.roundid,
                    heat=heat.heat,
                    status=heat.status
                )
                for heat in heats
            ]
            
            return HeatsGeneratedResponse(
                round_id=data.round_id,
                round_name=round_obj.name,
                heats_created=len(heats),
                heats=heat_responses
            )
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to create championship heats: {str(e)}")
    
    @get("/standings", status_code=HTTP_200_OK)
    async def get_standings(
        self,
        session: AsyncSession = Dependency(),
        division_id: Optional[int] = Parameter(None, query="division_id", description="Filter by division ID")
    ) -> List[RacerStanding]:
        """Get race standings based on all completed heats"""
        try:
            scheduler = RaceScheduler(session)
            standings = await scheduler.get_race_standings(division_id=division_id)
            
            # Convert to response model
            return [RacerStanding(**standing) for standing in standings]
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to get standings: {str(e)}")