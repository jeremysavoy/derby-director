# backend/api/services/timer/fasttrack.py
"""
FastTrack timer implementation for Derby Director
"""

import asyncio
import json
import logging
from typing import Dict, List, Optional, Any
import serial_asyncio

from .base import TimerInterface

logger = logging.getLogger(__name__)


class FastTrackTimer(TimerInterface):
    """Implementation for FastTrack timer hardware"""
    
    def __init__(self, port: str, baudrate: int = 9600, timeout: float = 1.0):
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self._reader = None
        self._writer = None
        self._connected = False
        self._lock = asyncio.Lock()
    
    async def connect(self) -> bool:
        """Connect to the FastTrack timer via serial port"""
        try:
            self._reader, self._writer = await serial_asyncio.open_serial_connection(
                url=self.port,
                baudrate=self.baudrate
            )
            self._connected = True
            logger.info(f"Connected to FastTrack timer on {self.port}")
            
            # Verify connection with identification command
            response = await self._send_command("ID")
            if not response or "FASTTRACK" not in response.upper():
                logger.error("Connected device does not appear to be a FastTrack timer")
                await self.disconnect()
                return False
                
            return True
        except Exception as e:
            logger.error(f"Failed to connect to FastTrack timer: {str(e)}")
            self._connected = False
            return False
    
    async def disconnect(self) -> None:
        """Disconnect from the FastTrack timer"""
        if self._writer:
            self._writer.close()
            await asyncio.sleep(0.1)  # Give it time to close
        self._connected = False
        self._reader = None
        self._writer = None
        logger.info("Disconnected from FastTrack timer")
    
    async def _send_command(self, command: str, wait_for_response: bool = True) -> Optional[str]:
        """Send a command to the timer and optionally wait for a response"""
        if not self._connected or not self._writer:
            logger.error("Cannot send command - not connected to FastTrack timer")
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
                logger.error(f"Error sending command {command} to FastTrack timer: {str(e)}")
                return None
    
    async def reset(self) -> bool:
        """Reset the FastTrack timer"""
        response = await self._send_command("RESET")
        return response == "RESET OK"
    
    async def prepare_heat(self, lanes: List[Dict[str, Any]]) -> bool:
        """Prepare the FastTrack timer for a new heat"""
        # FastTrack uses a different format for setup
        cmd = "SETUP"
        for lane_data in lanes:
            lane = lane_data.get("lane")
            racer_id = lane_data.get("racer_id")
            cmd += f":{lane}={racer_id}"
        
        response = await self._send_command(cmd)
        if response != "SETUP OK":
            logger.error("Failed to prepare FastTrack timer for heat")
            return False
            
        return True
    
    async def start_heat(self) -> bool:
        """Start the current heat on FastTrack timer"""
        # FastTrack has a two-step start process
        await self._send_command("ARM", wait_for_response=False)
        await asyncio.sleep(0.5)  # Wait for arming
        
        response = await self._send_command("START")
        if response != "RACE STARTED":
            logger.error("Failed to start heat on FastTrack timer")
            return False
            
        return True
    
    async def get_results(self) -> List[Dict[str, Any]]:
        """Get results from the FastTrack timer"""
        response = await self._send_command("GET RESULTS")
        if not response:
            logger.error("Failed to get results from FastTrack timer")
            return []
        
        try:
            # FastTrack returns JSON-formatted results
            result_data = json.loads(response)
            results = []
            
            for lane_result in result_data:
                results.append({
                    "lane": int(lane_result["lane"]),
                    "time": float(lane_result["time"]),
                    "place": int(lane_result["place"])
                })
                
            return results
        except Exception as e:
            logger.error(f"Error parsing FastTrack timer results: {str(e)}")
            return []
    
    @property
    def is_connected(self) -> bool:
        """Check if the timer is connected"""
        return self._connected