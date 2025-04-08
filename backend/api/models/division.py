# backend/api/models/division.py
"""
Division model for Derby Director
"""

from typing import List, TYPE_CHECKING
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship, Mapped

from .base import Base

if TYPE_CHECKING:
    from .racer import Racer


class Division(Base):
    """Model representing a racer division"""
    __tablename__ = "divisions"
    
    id: Mapped[int] = Column(Integer, primary_key=True)
    name: Mapped[str] = Column(String(100), unique=True)
    sort_order: Mapped[int] = Column(Integer, default=0)
    
    # Relationships
    racers: Mapped[List["Racer"]] = relationship("Racer", back_populates="racer_division")
    
    def __repr__(self) -> str:
        return f"<Division(id={self.id}, name='{self.name}')>"