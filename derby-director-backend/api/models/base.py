# derby_director/api/models/base.py
"""
Base model and database configuration for Derby Director
"""

from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase


class Base(AsyncAttrs, DeclarativeBase):
    """Base class for all models"""
    pass