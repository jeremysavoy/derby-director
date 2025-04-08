# backend/api/schemas/__init__.py
"""
Schema imports and aggregation for Derby Director
"""

from .racer import (
    RacerBase, RacerCreate, RacerUpdate,
    RacerResponse, RacerDetail
)

from .division import (
    DivisionBase, DivisionCreate, DivisionResponse,
    DivisionUpdate
)

from .heat import (
    LaneAssignment, HeatBase, HeatCreate,
    HeatUpdate, HeatResponse, LaneAssignmentResponse,
    HeatDetail
)

from .result import (
    ResultBase, ResultCreate, ResultUpdate,
    ResultResponse, ResultDetail, HeatResultRequest,
    HeatResultsResponse
)

from .auth import (
    LoginRequest, TokenResponse, UserInfo
)

# List of all schemas for easy import
__all__ = [
    # Racer schemas
    'RacerBase', 'RacerCreate', 'RacerUpdate',
    'RacerResponse', 'RacerDetail',
    
    # Division schemas
    'DivisionBase', 'DivisionCreate', 'DivisionUpdate',
    'DivisionResponse',
    
    # Heat schemas
    'LaneAssignment', 'HeatBase', 'HeatCreate',
    'HeatUpdate', 'HeatResponse', 'LaneAssignmentResponse',
    'HeatDetail',
    
    # Result schemas
    'ResultBase', 'ResultCreate', 'ResultUpdate',
    'ResultResponse', 'ResultDetail', 'HeatResultRequest',
    'HeatResultsResponse',
    
    # Auth schemas
    'LoginRequest', 'TokenResponse', 'UserInfo',
]