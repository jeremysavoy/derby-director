# derby_director/api/controllers/auth.py
"""
Authentication controller for Derby Director
"""

from typing import AsyncGenerator, Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from litestar import post, get
from litestar.controller import Controller
from litestar.di import Provide
from litestar.params import Dependency
from litestar.exceptions import NotAuthorizedException, NotFoundException
from litestar.status_codes import HTTP_200_OK
from typing import Annotated

from backend.api.schemas import LoginRequest, TokenResponse, UserInfo
from backend.api.models import Settings
from backend.api.middleware.auth import create_access_token, get_jwt_user


async def provide_session() -> AsyncGenerator[AsyncSession, None]:
    """Dependency provider for database session"""
    from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
    from backend.config import DATABASE_URL
    
    engine = create_async_engine(DATABASE_URL)
    async_session = async_sessionmaker(engine, expire_on_commit=False)
    
    async with async_session() as session:
        yield session


class AuthController(Controller):
    """Controller for authentication endpoints"""
    
    path = "/auth"
    dependencies = {"session": Provide(provide_session),
                    "user": get_jwt_user
    }
    
    @post("/login", status_code=HTTP_200_OK)
    async def login(
        self, 
        data: LoginRequest,
        session: AsyncSession = Dependency()
    ) -> TokenResponse:
        """Authenticate user and return JWT token"""
        # In a real app, verify against users table
        # For now, check against settings for admin password
        try:
            # Get admin password from settings
            result = await session.execute(
                select(Settings).filter(Settings.key == "admin_password")
            )
            password_setting = result.scalar_one_or_none()
            
            if not password_setting or data.password != password_setting.value:
                raise NotAuthorizedException("Invalid username or password")
            
            # Only allow "admin" username for now
            if data.username != "admin":
                raise NotAuthorizedException("Invalid username or password")
            
            # Create access token
            access_token = create_access_token(
                user_id="admin",
                username="admin",
                is_admin=True
            )
            
            return TokenResponse(access_token=access_token)
            
        except Exception as e:
            if isinstance(e, NotAuthorizedException):
                raise
            raise NotAuthorizedException("Authentication failed")
    
    @get("/me", status_code=HTTP_200_OK)
    async def get_current_user(
        self,
        user: Annotated[dict, Dependency()]
    ) -> UserInfo:
        """Get current user info from JWT token"""
        return UserInfo(
            id=user["id"],
            username=user["username"],
            is_admin=user["is_admin"]
        )