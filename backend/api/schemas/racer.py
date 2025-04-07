# derby_director/api/schemas/racer.py
"""
Racer schemas for API requests and responses
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class RacerBase(BaseModel):
    """Base schema for racer data"""
    firstname: str = Field(..., description="Racer's first name")
    lastname: str = Field(..., description="Racer's last name")
    divisionid: int = Field(..., description="ID of the racer's division")
    rankid: Optional[int] = Field(None, description="ID of the racer's rank (if applicable)")
    carno: Optional[str] = Field(None, description="Car number")
    carname: Optional[str] = Field(None, description="Car name")


class RacerCreate(RacerBase):
    """Schema for creating a new racer"""
    pass


class RacerUpdate(RacerBase):
    """Schema for updating an existing racer"""
    firstname: Optional[str] = Field(None, description="Racer's first name")
    lastname: Optional[str] = Field(None, description="Racer's last name")
    divisionid: Optional[int] = Field(None, description="ID of the racer's division")
    exclude: Optional[bool] = Field(None, description="Whether to exclude the racer")
    imagefile: Optional[str] = Field(None, description="Path to racer's image file")


class RacerResponse(RacerBase):
    """Schema for racer responses"""
    id: int = Field(..., description="Racer ID")
    exclude: bool = Field(False, description="Whether the racer is excluded from races")
    imagefile: Optional[str] = Field(None, description="Path to racer's image file")
    created_at: datetime = Field(..., description="When the racer was created")
    updated_at: datetime = Field(..., description="When the racer was last updated")
    
    class Config:
        from_attributes = True


class RacerDetail(RacerResponse):
    """Detailed racer schema including related division and rank info"""
    division_name: Optional[str] = Field(None, description="Name of racer's division")
    rank_name: Optional[str] = Field(None, description="Name of racer's rank")
    
    class Config:
        from_attributes = True