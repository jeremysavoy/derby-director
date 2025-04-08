# backend/api/models/heat.py
"""
Heat and RacerHeat models for Derby Director
"""

from datetime import datetime
from typing import List, Optional, TYPE_CHECKING
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship, Mapped

from .base import Base

if TYPE_CHECKING:
    from .round import Round
    from .racer import Racer
    from .result import RaceResult


class Heat(Base):
    """Model representing a single heat (race)"""
    __tablename__ = "heats"
    
    id: Mapped[int] = Column(Integer, primary_key=True)
    roundid: Mapped[int] = Column(Integer, ForeignKey("rounds.id"))
    heat: Mapped[int] = Column(Integer)  # Heat number within the round
    status: Mapped[str] = Column(String(20), default="scheduled")  # scheduled, in_progress, completed
    completed_time: Mapped[Optional[datetime]] = Column(DateTime, nullable=True)
    
    # Relationships
    round: Mapped["Round"] = relationship("Round", back_populates="heats")
    lanes: Mapped[List["RacerHeat"]] = relationship("RacerHeat", back_populates="heat")
    results: Mapped[List["RaceResult"]] = relationship("RaceResult", back_populates="heat")
    
    def __repr__(self) -> str:
        return f"<Heat(id={self.id}, heat={self.heat}, status='{self.status}')>"


class RacerHeat(Base):
    """Model representing a racer's assignment to a heat lane"""
    __tablename__ = "racer_heats"
    
    id: Mapped[int] = Column(Integer, primary_key=True)
    heat_id: Mapped[int] = Column(Integer, ForeignKey("heats.id"))
    lane: Mapped[int] = Column(Integer)  # Lane number
    racer_id: Mapped[int] = Column(Integer, ForeignKey("racers.id"))
    
    # Relationships
    heat: Mapped["Heat"] = relationship("Heat", back_populates="lanes")
    racer: Mapped["Racer"] = relationship("Racer")
    
    def __repr__(self) -> str:
        return f"<RacerHeat(heat_id={self.heat_id}, lane={self.lane}, racer_id={self.racer_id})>"