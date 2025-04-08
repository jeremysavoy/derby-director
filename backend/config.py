# backend/config.py
"""
Configuration for Derby Director
"""

import os
from pathlib import Path
from typing import Dict, Any, Optional

# Base directory
BASE_DIR = Path(__file__).resolve().parent

# Environment settings
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
DEBUG = ENVIRONMENT == "development"

# Database URL
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "sqlite+aiosqlite:///derby_director.db"
)

# JWT configuration
JWT_SECRET = os.getenv("JWT_SECRET", "your-secret-key-change-in-production")
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION = 24 * 60 * 60  # 24 hours in seconds

# CORS settings
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",")

# File storage
UPLOAD_DIR = BASE_DIR / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

# Application settings
APP_SETTINGS: Dict[str, Any] = {
    "title": "Derby Director API",
    "version": "1.0.0",
    "debug": DEBUG,
}

# Timer settings
DEFAULT_TIMER_CONFIG: Dict[str, Any] = {
    "timer_type": "smartline",
    "connection_type": "serial",
    "port": "",
    "baudrate": 9600,
    "lanes": 4,
}