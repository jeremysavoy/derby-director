# backend/api/schemas/division.py
"""
Division schemas for API requests and responses
"""

from typing import Optional
from pydantic import BaseModel, Field


class DivisionBase(BaseModel):
    """Base schema for division data"""
    name: str = Field(..., description="Division name")
    sort_order: int = Field(0, description="Display order for the division")


class DivisionCreate(DivisionBase):
    """Schema for creating a new division"""
    pass


class DivisionUpdate(DivisionBase):
    """Schema for updating an existing division"""
    name: Optional[str] = Field(None, description="Division name")
    sort_order: Optional[int] = Field(None, description="Display order for the division")


class DivisionResponse(DivisionBase):
    """Schema for division responses"""
    id: int = Field(..., description="Division ID")
    
    class Config:
        from_attributes = True