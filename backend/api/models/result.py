# backend/api/models/result.py
"""
Race Result model for Derby Director
"""

from typing import Optional, TYPE_CHECKING
from sqlalchemy import Column, Integer, Float, Boolean, ForeignKey
from sqlalchemy.orm import relationship, Mapped

from .base import Base

if TYPE_CHECKING:
    from .heat import Heat
    from .racer import Racer


class RaceResult(Base):
    """Model representing the result of a race for a single lane"""
    __tablename__ = "race_results"
    
    id: Mapped[int] = Column(Integer, primary_key=True)
    heat_id: Mapped[int] = Column(Integer, ForeignKey("heats.id"))
    racer_id: Mapped[int] = Column(Integer, ForeignKey("racers.id"))
    lane: Mapped[int] = Column(Integer)
    time: Mapped[Optional[float]] = Column(Float, nullable=True)  # Time in seconds
    place: Mapped[Optional[int]] = Column(Integer, nullable=True)  # Finishing position
    completed: Mapped[bool] = Column(Boolean, default=False)
    
    # Relationships
    heat: Mapped["Heat"] = relationship("Heat", back_populates="results")
    racer: Mapped["Racer"] = relationship("Racer")
    
    def __repr__(self) -> str:
        return f"<RaceResult(heat_id={self.heat_id}, lane={self.lane}, time={self.time}, place={self.place})>"