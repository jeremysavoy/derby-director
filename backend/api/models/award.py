# derby_director/api/models/award.py
"""
Award models for Derby Director
"""

from typing import List, Optional, TYPE_CHECKING
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship, Mapped

from .base import Base

if TYPE_CHECKING:
    from .division import Division
    from .rank import Rank
    from .racer import Racer


class Award(Base):
    """Model representing an award type"""
    __tablename__ = "awards"
    
    id: Mapped[int] = Column(Integer, primary_key=True)
    title: Mapped[str] = Column(String(100))
    divisionid: Mapped[Optional[int]] = Column(Integer, ForeignKey("divisions.id"), nullable=True)
    rankid: Mapped[Optional[int]] = Column(Integer, ForeignKey("ranks.id"), nullable=True)
    awardtype: Mapped[str] = Column(String(20))  # speed, design, etc.
    sort_order: Mapped[int] = Column(Integer, default=0)
    
    # Relationships
    winners: Mapped[List["AwardWinner"]] = relationship("AwardWinner", back_populates="award")
    award_division: Mapped[Optional["Division"]] = relationship("Division")
    award_rank: Mapped[Optional["Rank"]] = relationship("Rank")
    
    def __repr__(self) -> str:
        return f"<Award(id={self.id}, title='{self.title}', type='{self.awardtype}')>"


class AwardWinner(Base):
    """Model representing a winner of an award"""
    __tablename__ = "award_winners"
    
    id: Mapped[int] = Column(Integer, primary_key=True)
    award_id: Mapped[int] = Column(Integer, ForeignKey("awards.id"))
    racer_id: Mapped[int] = Column(Integer, ForeignKey("racers.id"))
    place: Mapped[int] = Column(Integer)
    
    # Relationships
    award: Mapped["Award"] = relationship("Award", back_populates="winners")
    racer: Mapped["Racer"] = relationship("Racer")
    
    def __repr__(self) -> str:
        return f"<AwardWinner(award_id={self.award_id}, racer_id={self.racer_id}, place={self.place})>"