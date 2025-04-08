# derby_director/api/models/car.py
"""
Car model for Derby Director
"""

from typing import Optional, TYPE_CHECKING
from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship, Mapped

from .base import Base

if TYPE_CHECKING:
    from .racer import Racer


class Car(Base):
    """Model representing a car in the derby"""
    __tablename__ = "cars"
    
    id: Mapped[int] = Column(Integer, primary_key=True)
    racer_id: Mapped[int] = Column(Integer, ForeignKey("racers.id"), unique=True)
    weight: Mapped[Optional[float]] = Column(Float, nullable=True)
    car_number: Mapped[str] = Column(String(20))
    color: Mapped[Optional[str]] = Column(String(50), nullable=True)
    
    # Relationships
    racer: Mapped["Racer"] = relationship("Racer", back_populates="car")
    
    def __repr__(self) -> str:
        return f"<Car(id={self.id}, car_number='{self.car_number}', weight={self.weight})>"