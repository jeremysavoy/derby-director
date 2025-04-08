# derby_director/api/services/timer/base.py
"""
Base timer interface for Derby Director
"""

import logging
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Callable

logger = logging.getLogger(__name__)


class TimerInterface(ABC):
    """Abstract base class for timer hardware interfaces"""
    
    @abstractmethod
    async def connect(self) -> bool:
        """Connect to the timer hardware"""
        pass
    
    @abstractmethod
    async def disconnect(self) -> None:
        """Disconnect from the timer hardware"""
        pass
    
    @abstractmethod
    async def reset(self) -> bool:
        """Reset the timer"""
        pass
    
    @abstractmethod
    async def prepare_heat(self, lanes: List[Dict[str, Any]]) -> bool:
        """Prepare for a new heat with the specified lane assignments"""
        pass
    
    @abstractmethod
    async def start_heat(self) -> bool:
        """Start the current heat"""
        pass
    
    @abstractmethod
    async def get_results(self) -> List[Dict[str, Any]]:
        """Get results from the last heat"""
        pass
    
    @property
    @abstractmethod
    def is_connected(self) -> bool:
        """Check if the timer is connected"""
        pass


class TimerService:
    """Service for managing timer interfaces and handling race events"""
    
    def __init__(self):
        self.active_timer: Optional[TimerInterface] = None
        self.result_callbacks: List[Callable[[List[Dict[str, Any]]], None]] = []
    
    def register_callback(self, callback: Callable[[List[Dict[str, Any]]], None]) -> None:
        """Register a callback to be called when results are received"""
        self.result_callbacks.append(callback)
    
    async def initialize_timer(self, config: Dict[str, Any]) -> bool:
        """Initialize timer with given configuration"""
        # Close any existing timer first
        await self.close_timer()
        
        # Create new timer
        from .factory import TimerFactory
        timer = TimerFactory.create_timer(config)
        if not timer:
            return False
            
        # Try to connect
        success = await timer.connect()
        if success:
            self.active_timer = timer
            return True
        return False
    
    async def close_timer(self) -> None:
        """Close the active timer connection"""
        if self.active_timer:
            await self.active_timer.disconnect()
            self.active_timer = None
    
    async def run_heat(self, heat_data: Dict[str, Any]) -> Optional[List[Dict[str, Any]]]:
        """Run a complete heat and return results"""
        if not self.active_timer:
            logger.error("No active timer connection")
            return None
            
        # Reset the timer
        reset_ok = await self.active_timer.reset()
        if not reset_ok:
            logger.error("Failed to reset timer")
            return None
            
        # Prepare the heat with lane assignments
        lanes = heat_data.get("lanes", [])
        prepare_ok = await self.active_timer.prepare_heat(lanes)
        if not prepare_ok:
            logger.error("Failed to prepare heat")
            return None
            
        # Start the heat
        start_ok = await self.active_timer.start_heat()
        if not start_ok:
            logger.error("Failed to start heat")
            return None
            
        # Wait for completion and get results - this would be more sophisticated
        # in a real implementation with proper completion detection
        import asyncio
        await asyncio.sleep(1)  # Small delay to ensure timer has results
        
        results = await self.active_timer.get_results()
        
        # Call registered callbacks with results
        for callback in self.result_callbacks:
            try:
                callback(results)
            except Exception as e:
                logger.error(f"Error in result callback: {str(e)}")
                
        return results