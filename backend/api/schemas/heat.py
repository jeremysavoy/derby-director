# backend/api/schemas/heat.py
"""
Heat schemas for API requests and responses
"""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class LaneAssignment(BaseModel):
    """Schema for lane assignments"""
    lane: int = Field(..., description="Lane number")
    racer_id: int = Field(..., description="ID of the racer assigned to this lane")


class HeatBase(BaseModel):
    """Base schema for heat data"""
    roundid: int = Field(..., description="ID of the round this heat belongs to")
    heat: int = Field(..., description="Heat number within the round")


class HeatCreate(HeatBase):
    """Schema for creating a new heat"""
    lanes: List[LaneAssignment] = Field([], description="Lane assignments for this heat")


class HeatUpdate(BaseModel):
    """Schema for updating an existing heat"""
    status: Optional[str] = Field(None, description="Heat status (scheduled, in_progress, completed)")
    lanes: Optional[List[LaneAssignment]] = Field(None, description="Lane assignments to update")


class HeatResponse(HeatBase):
    """Schema for heat responses"""
    id: int = Field(..., description="Heat ID")
    status: str = Field(..., description="Heat status")
    completed_time: Optional[datetime] = Field(None, description="When the heat was completed")
    
    class Config:
        from_attributes = True


class LaneAssignmentResponse(LaneAssignment):
    """Schema for lane assignment responses with racer details"""
    racer_name: str = Field(..., description="Name of the racer")
    car_number: Optional[str] = Field(None, description="Car number")
    
    class Config:
        from_attributes = True


class HeatDetail(HeatResponse):
    """Detailed heat schema including lane assignments"""
    lanes: List[LaneAssignmentResponse] = Field([], description="Lane assignments for this heat")
    round_name: str = Field(..., description="Name of the round")
    
    class Config:
        from_attributes = True