# backend/api/models/racer.py
"""
Racer model for Derby Director
"""

from datetime import datetime
from typing import Optional, List, TYPE_CHECKING
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship, Mapped

from .base import Base

if TYPE_CHECKING:
    from .division import Division
    from .rank import Rank
    from .car import Car


class Racer(Base):
    """Model representing a racer (participant)"""
    __tablename__ = "racers"
    
    id: Mapped[int] = Column(Integer, primary_key=True)
    firstname: Mapped[str] = Column(String(100))
    lastname: Mapped[str] = Column(String(100))
    divisionid: Mapped[int] = Column(Integer, ForeignKey("divisions.id"))
    rankid: Mapped[Optional[int]] = Column(Integer, ForeignKey("ranks.id"), nullable=True)
    carno: Mapped[Optional[str]] = Column(String(20), nullable=True)
    carname: Mapped[Optional[str]] = Column(String(200), nullable=True)
    exclude: Mapped[bool] = Column(Boolean, default=False)
    imagefile: Mapped[Optional[str]] = Column(String(255), nullable=True)
    created_at: Mapped[datetime] = Column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    racer_division: Mapped["Division"] = relationship("Division", back_populates="racers")
    rank: Mapped[Optional["Rank"]] = relationship("Rank", back_populates="racers")
    car: Mapped[Optional["Car"]] = relationship("Car", back_populates="racer", uselist=False)
    
    @property
    def fullname(self) -> str:
        """Get the racer's full name"""
        return f"{self.firstname} {self.lastname}"
    
    def __repr__(self) -> str:
        return f"<Racer(id={self.id}, name='{self.fullname}', carno='{self.carno}')>"