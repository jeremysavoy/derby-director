# backend/api/services/timer/factory.py
"""
Timer factory for creating appropriate timer instances
"""

import logging
from typing import Dict, Any, Optional

from .base import TimerInterface

logger = logging.getLogger(__name__)


class TimerFactory:
    """Factory for creating appropriate timer interface instances"""
    
    @staticmethod
    def create_timer(config: Dict[str, Any]) -> Optional[TimerInterface]:
        """Create a timer interface based on configuration"""
        timer_type = config.get("timer_type", "").lower()
        connection_type = config.get("connection_type", "").lower()
        
        if not timer_type or not connection_type:
            logger.error("Missing timer type or connection type in configuration")
            return None
        
        # Handle serial connections
        if connection_type == "serial":
            port = config.get("port")
            baudrate = int(config.get("baudrate", 9600))
            
            if not port:
                logger.error("Missing serial port in configuration")
                return None
                
            if timer_type == "smartline":
                from .smartline import SmartLineTimer
                return SmartLineTimer(port, baudrate)
                
            elif timer_type == "fasttrack":
                from .fasttrack import FastTrackTimer
                return FastTrackTimer(port, baudrate)
                
            elif timer_type == "newbold":
                # Placeholder for future implementation
                logger.error("NewBold timer not yet implemented")
                return None
                
        # Handle network connections
        elif connection_type == "network":
            host = config.get("host")
            port = int(config.get("port", 0))
            
            if not host or not port:
                logger.error("Missing host or port in configuration")
                return None
            
            # Placeholder for network timer implementations
            logger.error(f"Network timer type '{timer_type}' not implemented")
            return None
            
        logger.error(f"Unsupported timer type: {timer_type} with connection: {connection_type}")
        return None