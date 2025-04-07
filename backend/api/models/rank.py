# derby_director/api/models/rank.py
"""
Rank model for Derby Director
"""

from typing import List, TYPE_CHECKING
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship, Mapped

from .base import Base

if TYPE_CHECKING:
    from .racer import Racer


class Rank(Base):
    """Model representing a rank (e.g. Lion, Tiger, Wolf, Bear, Webelos and Arrow of Light in Cub Scouts)"""
    __tablename__ = "ranks"
    
    id: Mapped[int] = Column(Integer, primary_key=True)
    name: Mapped[str] = Column(String(100), unique=True)
    sort_order: Mapped[int] = Column(Integer, default=0)
    
    # Relationships
    racers: Mapped[List["Racer"]] = relationship("Racer", back_populates="rank")
    
    def __repr__(self) -> str:
        return f"<Rank(id={self.id}, name='{self.name}')>"