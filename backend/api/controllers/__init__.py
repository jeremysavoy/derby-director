# backend/api/controllers/__init__.py
"""
Controller imports and aggregation for Derby Director
"""

from .auth import AuthController
from .racers import RacerController
from .divisions import DivisionController
from .heats import HeatController
from .results import ResultController
from .rounds import RoundController  # Add the new RoundController

# List of all controllers for easy import
__all__ = [
    "AuthController",
    "RacerController",
    "DivisionController",
    "HeatController",
    "ResultController",
    "RoundController",  # Add to __all__ list
]