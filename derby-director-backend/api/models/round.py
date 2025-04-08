# derby_director/api/models/round.py
"""
Round model for Derby Director
"""

from typing import List, Optional, TYPE_CHECKING
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship, Mapped

from .base import Base

if TYPE_CHECKING:
    from .division import Division
    from .heat import Heat


class Round(Base):
    """Model representing a round of racing"""
    __tablename__ = "rounds"
    
    id: Mapped[int] = Column(Integer, primary_key=True)
    name: Mapped[str] = Column(String(100))
    divisionid: Mapped[Optional[int]] = Column(Integer, ForeignKey("divisions.id"), nullable=True)
    roundno: Mapped[int] = Column(Integer)
    phase: Mapped[str] = Column(String(50), default="normal")  # normal, final, semifinal, etc.
    charttype: Mapped[str] = Column(String(50), default="roster")  # roster, elimination, etc.
    
    # Relationships
    heats: Mapped[List["Heat"]] = relationship("Heat", back_populates="round")
    round_division: Mapped[Optional["Division"]] = relationship("Division")
    
    def __repr__(self) -> str:
        return f"<Round(id={self.id}, name='{self.name}', phase='{self.phase}')>"