# derby_director/api/services/timer/smartline.py
"""
SmartLine timer implementation for Derby Director
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
import serial_asyncio

from .base import TimerInterface

logger = logging.getLogger(__name__)


class SmartLineTimer(TimerInterface):
    """Implementation for SmartLine timer hardware"""
    
    def __init__(self, port: str, baudrate: int = 9600, timeout: float = 1.0):
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self._reader = None
        self._writer = None
        self._connected = False
        self._lock = asyncio.Lock()
    
    async def connect(self) -> bool:
        """Connect to the SmartLine timer via serial port"""
        try:
            self._reader, self._writer = await serial_asyncio.open_serial_connection(
                url=self.port,
                baudrate=self.baudrate
            )
            self._connected = True
            logger.info(f"Connected to SmartLine timer on {self.port}")
            
            # Send a reset command to ensure timer is ready
            reset_success = await self.reset()
            if not reset_success:
                logger.warning("Failed to reset timer during connection")
                
            return True
        except Exception as e:
            logger.error(f"Failed to connect to SmartLine timer: {str(e)}")
            self._connected = False
            return False
    
    async def disconnect(self) -> None:
        """Disconnect from the SmartLine timer"""
        if self._writer:
            self._writer.close()
            await asyncio.sleep(0.1)  # Give it time to close
        self._connected = False
        self._reader = None
        self._writer = None
        logger.info("Disconnected from SmartLine timer")
    
    async def _send_command(self, command: str, wait_for_response: bool = True) -> Optional[str]:
        """Send a command to the timer and optionally wait for a response"""
        if not self._connected or not self._writer:
            logger.error("Cannot send command - not connected to SmartLine timer")
            return None
        
        async with self._lock:  # Ensure only one command at a time
            try:
                # Send the command with proper line ending
                cmd = f"{command}\r\n"
                self._writer.write(cmd.encode())
                await self._writer.drain()
                
                if wait_for_response and self._reader:
                    # Wait for response with timeout
                    response_future = asyncio.create_task(self._reader.readline())
                    try:
                        response = await asyncio.wait_for(response_future, self.timeout)
                        return response.decode().strip()
                    except asyncio.TimeoutError:
                        logger.error(f"Timeout waiting for response to command: {command}")
                        return None
                return None
            except Exception as e:
                logger.error(f"Error sending command {command} to SmartLine timer: {str(e)}")
                return None
    
    async def reset(self) -> bool:
        """Reset the SmartLine timer"""
        response = await self._send_command("R")
        return response == "OK"
    
    async def prepare_heat(self, lanes: List[Dict[str, Any]]) -> bool:
        """Prepare the SmartLine timer for a new heat"""
        # Configure each lane with racer info
        for lane_data in lanes:
            lane = lane_data.get("lane")
            racer_id = lane_data.get("racer_id")
            cmd = f"L{lane},{racer_id}"
            response = await self._send_command(cmd)
            if response != "OK":
                logger.error(f"Failed to set lane {lane} for racer {racer_id}")
                return False
        
        # Tell timer we're ready
        response = await self._send_command("READY")
        if response != "OK":
            logger.error("Failed to prepare timer for heat")
            return False
            
        return True
    
    async def start_heat(self) -> bool:
        """Start the current heat on SmartLine timer"""
        response = await self._send_command("GO")
        if response != "STARTED":
            logger.error("Failed to start heat")
            return False
            
        return True
    
    async def get_results(self) -> List[Dict[str, Any]]:
        """Get results from the SmartLine timer"""
        response = await self._send_command("RESULTS")
        if not response:
            logger.error("Failed to get results from timer")
            return []
        
        # Parse the results string
        # Format example: "1,2.345,2,2.456,3,2.567,4,2.678"
        # Where it's lane,time,lane,time,etc.
        try:
            parts = response.split(",")
            results = []
            
            for i in range(0, len(parts), 2):
                if i+1 < len(parts):
                    lane = int(parts[i])
                    time = float(parts[i+1])
                    results.append({
                        "lane": lane,
                        "time": time
                    })
            
            # Sort by time to calculate places
            results.sort(key=lambda x: x["time"])
            for place, result in enumerate(results, 1):
                result["place"] = place
                
            return results
        except Exception as e:
            logger.error(f"Error parsing SmartLine timer results: {str(e)}")
            return []
    
    @property
    def is_connected(self) -> bool:
        """Check if the timer is connected"""
        return self._connected