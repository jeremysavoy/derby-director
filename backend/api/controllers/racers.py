# derby_director/api/controllers/racers.py
"""
Racer controller for Derby Director
"""

from typing import Annotated, List, Optional, AsyncGenerator, Any

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from litestar import get, post, put, delete
from litestar.controller import Controller
from litestar.di import Provide
from litestar.params import Dependency, Parameter as Query
from litestar.exceptions import NotFoundException
from litestar.status_codes import HTTP_200_OK, HTTP_201_CREATED, HTTP_204_NO_CONTENT

from backend.api.models import Racer, Division, Rank
from backend.api.schemas import (
    RacerCreate, RacerUpdate, RacerResponse, RacerDetail
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


class RacerController(Controller):
    """Controller for racer-related endpoints"""
    
    path = "/racers"
    dependencies = {"session": Provide(provide_session),
                    "user": get_jwt_user
    }
    
    @get("/", status_code=HTTP_200_OK)
    async def get_racers(
        self,
        session: Annotated[AsyncSession, Dependency()],
        division_id: Annotated[Optional[int], Query(description="Filter by division ID")] = None,
        rank_id: Annotated[Optional[int], Query(description="Filter by rank ID")] = None,
        exclude_status: Annotated[Optional[bool], Query(description="Filter by exclude status")] = None,
        search: Annotated[Optional[str], Query(description="Search by name or car number")] = None
    ) -> List[RacerResponse]:
        """Get all racers with optional filtering"""
        query = select(Racer)
        
        # Apply filters
        if division_id is not None:
            query = query.filter(Racer.divisionid == division_id)
            
        if rank_id is not None:
            query = query.filter(Racer.rankid == rank_id)
            
        if exclude_status is not None:
            query = query.filter(Racer.exclude == exclude_status)
            
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                (func.lower(Racer.firstname).like(search_term)) |
                (func.lower(Racer.lastname).like(search_term)) |
                (func.lower(Racer.carno).like(search_term))
            )
        
        # Execute query
        result = await session.execute(query)
        racers = result.scalars().all()
        
        return [RacerResponse.model_validate(racer) for racer in racers]
    
    @get("/{racer_id:int}", status_code=HTTP_200_OK)
    async def get_racer(
        self,
        racer_id: int,
        session: Annotated[AsyncSession, Dependency()]
    ) -> RacerDetail:
        """Get a single racer by ID with division and rank details"""
        query = (
            select(Racer, Division.name.label("division_name"), Rank.name.label("rank_name"))
            .outerjoin(Division, Racer.divisionid == Division.id)
            .outerjoin(Rank, Racer.rankid == Rank.id)
            .filter(Racer.id == racer_id)
        )
        
        result = await session.execute(query)
        row = result.one_or_none()
        
        if not row:
            raise NotFoundException(f"Racer with ID {racer_id} not found")
        
        racer, division_name, rank_name = row
        
        # Create response model
        response = RacerDetail.model_validate(racer)
        response.division_name = division_name
        response.rank_name = rank_name
        
        return response
    
    @post("/", status_code=HTTP_201_CREATED)
    async def create_racer(
        self,
        data: RacerCreate,
        session: Annotated[AsyncSession, Dependency()],
        user: Annotated[dict, Dependency()]
    ) -> RacerResponse:
        """Create a new racer"""
        # Create racer instance
        racer = Racer(**data.model_dump())
        
        # Add to database
        session.add(racer)
        await session.commit()
        await session.refresh(racer)
        
        return RacerResponse.model_validate(racer)
    
    @put("/{racer_id:int}", status_code=HTTP_200_OK)
    async def update_racer(
        self,
        racer_id: int,
        data: RacerUpdate,
        session: Annotated[AsyncSession, Dependency()],
        user: Annotated[dict, Dependency()]
    ) -> RacerResponse:
        """Update an existing racer"""
        # Get racer
        racer = await session.get(Racer, racer_id)
        if not racer:
            raise NotFoundException(f"Racer with ID {racer_id} not found")
        
        # Update fields
        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(racer, key, value)
        
        # Save changes
        await session.commit()
        await session.refresh(racer)
        
        return RacerResponse.model_validate(racer)
    
    @delete("/{racer_id:int}", status_code=HTTP_204_NO_CONTENT)
    async def delete_racer(
        self,
        racer_id: int,
        session: Annotated[AsyncSession, Dependency()],
        user: Annotated[dict, Dependency()]
    ) -> None:
        """Delete a racer"""
        # Get racer
        racer = await session.get(Racer, racer_id)
        if not racer:
            raise NotFoundException(f"Racer with ID {racer_id} not found")
        
        # Delete
        await session.delete(racer)
        await session.commit()