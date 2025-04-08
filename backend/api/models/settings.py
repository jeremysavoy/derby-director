# backend/api/models/settings.py
"""
Settings model for Derby Director
"""

from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import Mapped

from .base import Base


class Settings(Base):
    """Model for application settings"""
    __tablename__ = "settings"
    
    id: Mapped[int] = Column(Integer, primary_key=True)
    key: Mapped[str] = Column(String(100), unique=True)
    value: Mapped[str] = Column(Text)
    
    def __repr__(self) -> str:
        return f"<Settings(key='{self.key}')>"


class TimerConfiguration(Base):
    """Model for timer hardware configuration"""
    __tablename__ = "timer_configuration"
    
    id: Mapped[int] = Column(Integer, primary_key=True)
    timer_type: Mapped[str] = Column(String(50))  # SmartLine, FastTrack, etc.
    connection_type: Mapped[str] = Column(String(20))  # serial, network
    connection_details: Mapped[str] = Column(Text)  # JSON with connection parameters
    lanes: Mapped[int] = Column(Integer)
    is_active: Mapped[bool] = Column(Integer, default=0)  # SQLite doesn't have a boolean type
    
    @property
    def connection_params(self):
        """Parse connection details JSON"""
        import json
        return json.loads(self.connection_details)
    
    def __repr__(self) -> str:
        return f"<TimerConfiguration(id={self.id}, type='{self.timer_type}')>"