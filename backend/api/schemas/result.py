# backend/api/schemas/result.py
"""
Race result schemas for API requests and responses
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class ResultBase(BaseModel):
    """Base schema for race result data"""
    heat_id: int = Field(..., description="ID of the heat")
    racer_id: int = Field(..., description="ID of the racer")
    lane: int = Field(..., description="Lane number")
    time: Optional[float] = Field(None, description="Race time in seconds")
    place: Optional[int] = Field(None, description="Finishing position")


class ResultCreate(ResultBase):
    """Schema for creating a new result"""
    pass


class ResultUpdate(BaseModel):
    """Schema for updating an existing result"""
    time: Optional[float] = Field(None, description="Race time in seconds")
    place: Optional[int] = Field(None, description="Finishing position")
    completed: Optional[bool] = Field(None, description="Whether the result is final")


class ResultResponse(ResultBase):
    """Schema for result responses"""
    id: int = Field(..., description="Result ID")
    completed: bool = Field(..., description="Whether the result is final")
    
    class Config:
        from_attributes = True


class ResultDetail(ResultResponse):
    """Detailed result schema including racer details"""
    racer_name: str = Field(..., description="Name of the racer")
    car_number: Optional[str] = Field(None, description="Car number")
    heat_number: int = Field(..., description="Heat number")
    round_name: str = Field(..., description="Name of the round")
    
    class Config:
        from_attributes = True


class HeatResultRequest(BaseModel):
    """Schema for submitting multiple results for a heat"""
    heat_id: int = Field(..., description="ID of the heat")
    results: List[ResultCreate] = Field(..., description="List of results for each lane")


class HeatResultsResponse(BaseModel):
    """Schema for heat results summary"""
    heat_id: int = Field(..., description="Heat ID")
    round_name: str = Field(..., description="Name of the round")
    heat_number: int = Field(..., description="Heat number")
    results: List[ResultDetail] = Field(..., description="Results for each lane")
    completed: bool = Field(..., description="Whether all results are final")