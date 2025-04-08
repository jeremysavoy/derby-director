# derby_director/api/schemas/auth.py
"""
Authentication schemas for API requests and responses
"""

from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    """Schema for login requests"""
    username: str = Field(..., description="Username")
    password: str = Field(..., description="Password")


class TokenResponse(BaseModel):
    """Schema for token responses"""
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field("bearer", description="Token type")


class UserInfo(BaseModel):
    """Schema for user information"""
    id: str = Field(..., description="User ID")
    username: str = Field(..., description="Username")
    is_admin: bool = Field(..., description="Whether the user is an admin")