# derby_director/api/middleware/auth.py
"""
Authentication middleware for Derby Director
"""

import time
from typing import Dict, Any, Optional
import jwt
from litestar.connection import ASGIConnection
from litestar.exceptions import NotAuthorizedException
from litestar.middleware import AbstractMiddleware
from litestar.datastructures import State

from backend.config import JWT_SECRET, JWT_ALGORITHM


async def get_jwt_user(state: State) -> Dict[str, Any]:
    """Get user details from JWT token in state"""
    user = state.jwt_payload.get("sub")
    if user is None:
        raise NotAuthorizedException("Invalid authentication credentials")
    
    return {
        "id": user,
        "username": state.jwt_payload.get("username", "unknown"),
        "is_admin": state.jwt_payload.get("is_admin", False)
    }


class JWTAuthMiddleware(AbstractMiddleware):
    """Middleware for JWT authentication"""
    
    async def __call__(
        self, 
        connection: ASGIConnection, 
        call_next: Any
    ) -> Any:
        """Process the request to extract and validate JWT token"""
        if connection.scope["type"] != "http":
            return await call_next(connection)
        
        # Skip auth for specified paths
        path = connection.scope["path"]
        if path.startswith(("/docs", "/openapi", "/login")):
            return await call_next(connection)
        
        # Get token from headers
        auth_header = connection.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return await call_next(connection)
        
        token = auth_header.replace("Bearer ", "")
        
        try:
            # Decode and validate token
            payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            
            # Check if token is expired
            if payload.get("exp") and time.time() > payload["exp"]:
                raise NotAuthorizedException("Token has expired")
            
            # Add payload to state for use in route handlers
            connection.scope["state"].jwt_payload = payload
            
        except jwt.PyJWTError as e:
            # Let unauthorized routes proceed, they'll handle auth checking
            if not getattr(connection.route_handler, "require_auth", True):
                return await call_next(connection)
            
            # Otherwise, raise exception for auth failure
            raise NotAuthorizedException(f"Invalid token: {str(e)}")
        
        # Continue with request
        return await call_next(connection)


def create_access_token(
    user_id: str, 
    username: str, 
    is_admin: bool = False,
    expiration: Optional[int] = None
) -> str:
    """Create a new JWT access token"""
    from datetime import datetime, timedelta
    
    if expiration is None:
        from backend.config import JWT_EXPIRATION
        expiration = JWT_EXPIRATION
    
    expire = datetime.utcnow() + timedelta(seconds=expiration)
    
    payload = {
        "sub": user_id,
        "username": username,
        "is_admin": is_admin,
        "exp": expire.timestamp()
    }
    
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)