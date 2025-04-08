# backend/api/controllers/divisions.py
"""
Divisions controller for Derby Director
"""

from typing import Annotated, List, AsyncGenerator, Any

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from litestar import get, post, put, delete
from litestar.controller import Controller
from litestar.di import Provide
from litestar.params import Dependency
from litestar.exceptions import NotFoundException
from litestar.status_codes import HTTP_200_OK, HTTP_201_CREATED, HTTP_204_NO_CONTENT

from backend.api.models import Division
from backend.api.schemas import DivisionCreate, DivisionUpdate, DivisionResponse
from backend.api.middleware.auth import get_jwt_user


async def provide_session() -> AsyncGenerator[AsyncSession, None]:
    """Dependency provider for database session"""
    from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
    from backend.config import DATABASE_URL
    
    engine = create_async_engine(DATABASE_URL)
    async_session = async_sessionmaker(engine, expire_on_commit=False)
    
    async with async_session() as session:
        yield session


class DivisionController(Controller):
    """Controller for division-related endpoints"""
    
    path = "/divisions"
    dependencies = {"session": Provide(provide_session),
                    "user": get_jwt_user
    }
    
    @get("/", status_code=HTTP_200_OK)
    async def get_divisions(
        self,
        session: Annotated[AsyncSession, Dependency()]
    ) -> List[DivisionResponse]:
        """Get all divisions"""
        query = select(Division).order_by(Division.sort_order)
        result = await session.execute(query)
        divisions = result.scalars().all()
        
        return [DivisionResponse.model_validate(dvsn) for dvsn in divisions]
    
    @get("/{division_id:int}", status_code=HTTP_200_OK)
    async def get_division(
        self,
        division_id: int,
        session: Annotated[AsyncSession, Dependency()]
    ) -> DivisionResponse:
        """Get a single division by ID"""
        dvsn = await session.get(Division, division_id)
        if not dvsn:
            raise NotFoundException(f"Division with ID {division_id} not found")
        
        return DivisionResponse.model_validate(dvsn)
    
    @post("/", status_code=HTTP_201_CREATED)
    async def create_division(
        self,
        data: DivisionCreate,
        session: Annotated[AsyncSession, Dependency()],
        user: Annotated[dict, Dependency()]
    ) -> DivisionResponse:
        """Create a new division"""
        # Create division instance
        dvsn = Division(**data.model_dump())
        
        # Add to database
        session.add(dvsn)
        await session.commit()
        await session.refresh(dvsn)
        
        return DivisionResponse.model_validate(dvsn)
    
    @put("/{division_id:int}", status_code=HTTP_200_OK)
    async def update_division(
        self,
        division_id: int,
        data: DivisionUpdate,
        session: Annotated[AsyncSession, Dependency()],
        user: Annotated[dict, Dependency()]
    ) -> DivisionResponse:
        """Update an existing division"""
        # Get division
        dvsn = await session.get(Division, division_id)
        if not dvsn:
            raise NotFoundException(f"Division with ID {division_id} not found")
        
        # Update fields
        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(dvsn, key, value)
        
        # Save changes
        await session.commit()
        await session.refresh(dvsn)
        
        return DivisionResponse.model_validate(dvsn)
    
    @delete("/{division_id:int}", status_code=HTTP_204_NO_CONTENT)
    async def delete_division(
        self,
        division_id: int,
        session: Annotated[AsyncSession, Dependency()],
        user: Annotated[dict, Dependency()]
    ) -> None:
        """Delete a division"""
        # Get division
        dvsn = await session.get(Division, division_id)
        if not dvsn:
            raise NotFoundException(f"Division with ID {division_id} not found")
        
        # Check if division has racers
        query = select(func.count()).select_from(Division).where(Division.id == division_id)
        result = await session.execute(query)
        count = result.scalar()
        
        if count > 0:
            # Don't allow deletion of divisions with racers
            from litestar.exceptions import ClientException
            raise ClientException(
                "Cannot delete division with associated racers. "
                "Remove or reassign racers first."
            )
        
        # Delete
        await session.delete(dvsn)
        await session.commit()