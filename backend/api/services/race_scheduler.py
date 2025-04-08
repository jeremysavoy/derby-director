# backend/api/services/race_scheduler.py
"""
Race scheduling service for Derby Director.

This module handles the logic for creating heats, scheduling racers,
ensuring fair lane assignments, and managing advancement between rounds.
"""

import random
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from backend.api.models import Round, Heat, Racer, RacerHeat, RaceResult, Division

logger = logging.getLogger(__name__)

class RaceScheduler:
    """
    Service for scheduling races, creating heats, and managing rounds.
    """
    
    def __init__(self, session: AsyncSession):
        """Initialize with a database session."""
        self.session = session
    
    async def create_preliminary_round(self, division_id: int, name: str = None) -> Round:
        """
        Create a preliminary round for a division.
        
        Args:
            division_id: The ID of the division to create a round for
            name: Optional name for the round (defaults to "{Division Name} Preliminary")
            
        Returns:
            The created Round object
        """
        # Verify division exists
        dvsn = await self.session.get(Division, division_id)
        if not dvsn:
            raise ValueError(f"Division with ID {division_id} not found")
            
        # Check if preliminary round already exists
        existing_query = select(Round).filter(
            Round.divisionid == division_id,
            Round.phase == "preliminary"
        )
        existing = await self.session.execute(existing_query)
        if existing.scalar_one_or_none():
            raise ValueError(f"Preliminary round for division {dvsn.name} already exists")
        
        # Get the highest round number for ordering
        max_round_query = select(func.max(Round.roundno)).where(Round.divisionid == division_id)
        max_round_result = await self.session.execute(max_round_query)
        max_round = max_round_result.scalar() or 0
        
        # Create round name if not provided
        if not name:
            name = f"{dvsn.name} Preliminary"
            
        # Create round
        round_obj = Round(
            name=name,
            divisionid=division_id,
            roundno=max_round + 1,
            phase="preliminary",
            charttype="roster"
        )
        
        self.session.add(round_obj)
        await self.session.flush()
        
        return round_obj
    
    async def create_final_round(self, division_id: int, name: str = None) -> Round:
        """
        Create a final round for a division.
        
        Args:
            division_id: The ID of the division to create a round for
            name: Optional name for the round (defaults to "{Division Name} Finals")
            
        Returns:
            The created Round object
        """
        # Verify division exists
        dvsn = await self.session.get(Division, division_id)
        if not dvsn:
            raise ValueError(f"Division with ID {division_id} not found")
            
        # Check if final round already exists
        existing_query = select(Round).filter(
            Round.divisionid == division_id,
            Round.phase == "final"
        )
        existing = await self.session.execute(existing_query)
        if existing.scalar_one_or_none():
            raise ValueError(f"Final round for division {dvsn.name} already exists")
        
        # Get the highest round number for ordering
        max_round_query = select(func.max(Round.roundno)).where(Round.divisionid == division_id)
        max_round_result = await self.session.execute(max_round_query)
        max_round = max_round_result.scalar() or 0
        
        # Create round name if not provided
        if not name:
            name = f"{dvsn.name} Finals"
            
        # Create round
        round_obj = Round(
            name=name,
            divisionid=division_id,
            roundno=max_round + 1,
            phase="final",
            charttype="roster"
        )
        
        self.session.add(round_obj)
        await self.session.flush()
        
        return round_obj
    
    async def create_championship_round(self, name: str = "Championship Finals") -> Round:
        """
        Create a championship round for the top racers across all divisions.
        
        Args:
            name: Optional name for the round
            
        Returns:
            The created Round object
        """
        # Get the highest round number for ordering
        max_round_query = select(func.max(Round.roundno))
        max_round_result = await self.session.execute(max_round_query)
        max_round = max_round_result.scalar() or 0
        
        # Create round
        round_obj = Round(
            name=name,
            divisionid=None,  # No specific division for championship
            roundno=max_round + 1,
            phase="championship",
            charttype="elimination"
        )
        
        self.session.add(round_obj)
        await self.session.flush()
        
        return round_obj
    
    async def generate_heats_for_round(
        self, 
        round_id: int, 
        lanes_per_heat: int = 4
    ) -> List[Heat]:
        """
        Generate heats for a round, assigning racers to lanes.
        For preliminary rounds, this will include all racers in the division.
        For final rounds, this will include top performers from preliminaries.
        
        Args:
            round_id: ID of the round to create heats for
            lanes_per_heat: Number of lanes on the track
            
        Returns:
            List of created Heat objects
        """
        # Get the round
        round_obj = await self.session.get(Round, round_id)
        if not round_obj:
            raise ValueError(f"Round with ID {round_id} not found")
        
        # Check if heats already exist for this round
        heat_count_query = select(func.count()).select_from(Heat).where(Heat.roundid == round_id)
        heat_count = await self.session.execute(heat_count_query)
        if heat_count.scalar() > 0:
            raise ValueError(f"Heats already exist for round {round_obj.name}")
        
        # Get racers based on round type
        racers = await self._get_racers_for_round(round_obj, lanes_per_heat)
        
        if not racers:
            raise ValueError(f"No eligible racers found for round {round_obj.name}")
        
        # Create heats and assign racers
        return await self._create_heats_with_racers(round_obj, racers, lanes_per_heat)
    
    async def _get_racers_for_round(
        self, 
        round_obj: Round, 
        lanes_per_heat: int
    ) -> List[Dict[str, Any]]:
        """
        Get racers for a round based on its type.
        
        For preliminary rounds: All non-excluded racers in the division
        For finals: Top performers from preliminary rounds
        For championship: Top performers from each division
        
        Returns a list of racer dicts with id and division information
        """
        if round_obj.phase == "preliminary":
            # For preliminary rounds, get all non-excluded racers in the division
            if round_obj.divisionid is None:
                raise ValueError("Preliminary rounds must be associated with a division")
                
            racer_query = (
                select(Racer)
                .where(
                    Racer.divisionid == round_obj.divisionid,
                    Racer.exclude == False
                )
                .order_by(Racer.id)
            )
            
            result = await self.session.execute(racer_query)
            racers = result.scalars().all()
            
            return [{"id": racer.id, "divisionid": racer.divisionid} for racer in racers]
            
        elif round_obj.phase == "final":
            # For final rounds, get top performers from preliminary rounds
            if round_obj.divisionid is None:
                raise ValueError("Final rounds must be associated with a division")
                
            # Find the preliminary round for this division
            prelim_query = select(Round).where(
                Round.divisionid == round_obj.divisionid,
                Round.phase == "preliminary"
            )
            prelim_result = await self.session.execute(prelim_query)
            prelim_round = prelim_result.scalar_one_or_none()
            
            if not prelim_round:
                raise ValueError(f"No preliminary round found for division {round_obj.divisionid}")
                
            # Get heats from preliminary round
            heats_query = select(Heat.id).where(Heat.roundid == prelim_round.id)
            heats_result = await self.session.execute(heats_query)
            heat_ids = [heat_id for (heat_id,) in heats_result]
            
            if not heat_ids:
                raise ValueError("No heats found in preliminary round")
            
            # Get top performers based on average time across all heats
            # This gets complex with SQL, so we'll fetch results and process in Python
            results_query = (
                select(
                    RaceResult.racer_id,
                    func.avg(RaceResult.time).label("avg_time"),
                    func.count(RaceResult.id).label("race_count"),
                    Racer.divisionid
                )
                .join(Racer, RaceResult.racer_id == Racer.id)
                .where(
                    RaceResult.heat_id.in_(heat_ids),
                    RaceResult.completed == True,
                    RaceResult.time.isnot(None)
                )
                .group_by(RaceResult.racer_id, Racer.divisionid)
                .order_by(func.avg(RaceResult.time))
            )
            
            results = await self.session.execute(results_query)
            racers_with_results = [
                {"id": racer_id, "avg_time": avg_time, "race_count": count, "divisionid": divisionid}
                for racer_id, avg_time, count, divisionid in results
            ]
            
            # Get the top performers based on track capacity
            # Calculate how many racers we need for the finals
            # For a 4-lane track, we typically want 4 or 8 racers depending on format
            top_count = lanes_per_heat * 2  # Usually we want 2 heats for finals
            
            # Make sure we have enough racers
            if len(racers_with_results) < lanes_per_heat:
                raise ValueError(f"Not enough racers with results for a final round (need at least {lanes_per_heat})")
                
            # Limit to top performers
            top_racers = racers_with_results[:min(top_count, len(racers_with_results))]
            
            return [{"id": racer["id"], "divisionid": racer["divisionid"]} for racer in top_racers]
            
        elif round_obj.phase == "championship":
            # For championship, get top performers from each division's final round
            # Get all divisions
            divisions_query = select(Division).order_by(Division.sort_order)
            divisions_result = await self.session.execute(divisions_query)
            divisions = divisions_result.scalars().all()
            
            top_racers = []
            for division in divisions:
                # Find the final round for this division
                final_query = select(Round).where(
                    Round.divisionid == division.id,
                    Round.phase == "final"
                )
                final_result = await self.session.execute(final_query)
                final_round = final_result.scalar_one_or_none()
                
                if not final_round:
                    continue  # Skip divisions without finals
                    
                # Get heats from this final round
                heats_query = select(Heat.id).where(Heat.roundid == final_round.id)
                heats_result = await self.session.execute(heats_query)
                heat_ids = [heat_id for (heat_id,) in heats_result]
                
                if not heat_ids:
                    continue  # Skip if no heats
                
                # Get the best performer from this division
                best_result_query = (
                    select(
                        RaceResult.racer_id,
                        func.avg(RaceResult.time).label("avg_time"),
                        Racer.divisionid
                    )
                    .join(Racer, RaceResult.racer_id == Racer.id)
                    .where(
                        RaceResult.heat_id.in_(heat_ids),
                        RaceResult.completed == True,
                        RaceResult.time.isnot(None)
                    )
                    .group_by(RaceResult.racer_id, Racer.divisionid)
                    .order_by(func.avg(RaceResult.time))
                    .limit(1)
                )
                
                best_result = await self.session.execute(best_result_query)
                top_racer = best_result.first()
                
                if top_racer:
                    racer_id, _, divisionid = top_racer
                    top_racers.append({"id": racer_id, "divisionid": divisionid})
            
            if not top_racers:
                raise ValueError("No qualifying racers found for championship round")
                
            return top_racers
            
        else:
            raise ValueError(f"Unsupported round phase: {round_obj.phase}")
    
    async def _create_heats_with_racers(
        self, 
        round_obj: Round, 
        racers: List[Dict[str, Any]], 
        lanes_per_heat: int
    ) -> List[Heat]:
        """
        Create heats for a round and assign racers to lanes.
        
        This method uses different strategies based on the round type:
        - For preliminary rounds: Distributes racers evenly, with random lane assignments
        - For finals: Assigns top performers based on their preliminary performance
        - For championship: Places division winners against each other
        
        Args:
            round_obj: The round to create heats for
            racers: List of racer dicts with id and divisionid
            lanes_per_heat: Number of lanes on the track
            
        Returns:
            List of created Heat objects
        """
        created_heats = []
        
        # For preliminary rounds, we want each racer to race the same number of times
        # and in different lanes for fairness
        if round_obj.phase == "preliminary":
            # Determine how many times each racer should race
            # Typically 3-4 times is good for preliminary rounds
            races_per_racer = 4
            
            # Create a lane assignment plan ensuring each racer races in different lanes
            lane_assignments = self._generate_balanced_lanes(racers, lanes_per_heat, races_per_racer)
            
            # Create heats based on the lane assignments
            heat_number = 1
            for heat_lanes in lane_assignments:
                heat = Heat(
                    roundid=round_obj.id,
                    heat=heat_number,
                    status="scheduled"
                )
                self.session.add(heat)
                await self.session.flush()
                
                # Assign racers to lanes
                for lane, racer_id in heat_lanes.items():
                    if racer_id is not None:  # Skip empty lanes
                        racer_heat = RacerHeat(
                            heat_id=heat.id,
                            lane=lane,
                            racer_id=racer_id
                        )
                        self.session.add(racer_heat)
                
                created_heats.append(heat)
                heat_number += 1
                
        # For finals and championship rounds, create heats based on preliminary performance
        elif round_obj.phase in ("final", "championship"):
            # For finals, we typically want 1 or 2 heats depending on number of racers
            heats_needed = (len(racers) + lanes_per_heat - 1) // lanes_per_heat
            
            # For finals with many qualifiers, we might want elimination rounds
            if round_obj.phase == "final" and len(racers) > lanes_per_heat * 2:
                # Implementation for elimination brackets would go here
                # For now, we'll just take the top performers
                racers = racers[:lanes_per_heat * 2]
                heats_needed = 2
                
            # Distribute racers into heats
            for heat_num in range(1, heats_needed + 1):
                heat = Heat(
                    roundid=round_obj.id,
                    heat=heat_num,
                    status="scheduled"
                )
                self.session.add(heat)
                await self.session.flush()
                
                # Determine which racers go in this heat
                start_idx = (heat_num - 1) * lanes_per_heat
                end_idx = min(start_idx + lanes_per_heat, len(racers))
                heat_racers = racers[start_idx:end_idx]
                
                # For finals, we want the fastest racers in the middle lanes
                # First, sort racers by their position in the input list (which is already sorted by performance)
                heat_racers_sorted = sorted(range(len(heat_racers)), key=lambda i: i)
                
                # Assign lanes - best racers get middle lanes
                lane_assignments = self._assign_lanes_by_rank(heat_racers_sorted, lanes_per_heat)
                
                for lane, idx in lane_assignments.items():
                    if idx < len(heat_racers):
                        racer_id = heat_racers[idx]["id"]
                        racer_heat = RacerHeat(
                            heat_id=heat.id,
                            lane=lane,
                            racer_id=racer_id
                        )
                        self.session.add(racer_heat)
                
                created_heats.append(heat)
        
        await self.session.commit()
        return created_heats
    
    def _generate_balanced_lanes(
        self, 
        racers: List[Dict[str, Any]], 
        lanes_per_heat: int, 
        races_per_racer: int
    ) -> List[Dict[int, int]]:
        """
        Generate a balanced lane assignment plan for preliminary rounds.
        
        This ensures:
        1. Each racer races the same number of times (races_per_racer)
        2. Each racer races in different lanes for fairness
        3. Each racer competes against different opponents
        
        Returns:
            List of dicts mapping lane numbers to racer IDs for each heat
        """
        num_racers = len(racers)
        racer_ids = [racer["id"] for racer in racers]
        
        # Track which lanes each racer has been assigned to
        racer_lanes = {racer_id: set() for racer_id in racer_ids}
        
        # Track how many times each racer has raced
        race_counts = {racer_id: 0 for racer_id in racer_ids}
        
        # Create a matrix to track which racers have raced against each other
        raced_against = {r1: set() for r1 in racer_ids}
        
        # Generate heats
        heats = []
        max_attempts = 1000  # Prevent infinite loops
        attempts = 0
        
        # Calculate total heats needed
        total_races = num_racers * races_per_racer
        lanes_per_heat = min(lanes_per_heat, num_racers)  # Can't have more lanes than racers
        total_slots = total_races // lanes_per_heat * lanes_per_heat
        
        # Adjust races_per_racer if necessary to ensure equal races
        if total_races % lanes_per_heat != 0:
            races_per_racer = (total_races // lanes_per_heat * lanes_per_heat) // num_racers
            total_races = num_racers * races_per_racer
        
        while sum(race_counts.values()) < total_races and attempts < max_attempts:
            attempts += 1
            
            # Create a new heat
            heat_lanes = {}
            heat_racers = []
            
            # Prioritize racers with fewer races
            eligible_racers = sorted(
                [r for r in racer_ids if race_counts[r] < races_per_racer],
                key=lambda r: (race_counts[r], len(racer_lanes[r]))
            )
            
            # Assign lanes for this heat
            for lane in range(1, lanes_per_heat + 1):
                # Find a racer who hasn't been in this lane before
                for racer_id in eligible_racers[:]:
                    # Check if racer hasn't raced in this lane yet
                    if lane not in racer_lanes[racer_id] and racer_id not in heat_racers:
                        # Check if racer hasn't raced against others in this heat
                        raced_against_current = False
                        for other_racer in heat_racers:
                            if other_racer in raced_against[racer_id]:
                                raced_against_current = True
                                break
                        
                        if not raced_against_current or attempts > max_attempts // 2:
                            heat_lanes[lane] = racer_id
                            heat_racers.append(racer_id)
                            racer_lanes[racer_id].add(lane)
                            race_counts[racer_id] += 1
                            eligible_racers.remove(racer_id)
                            break
            
            # If we assigned racers to lanes, add this heat
            if heat_lanes:
                # Update raced_against tracking
                for i, racer1 in enumerate(heat_racers):
                    for racer2 in heat_racers[i+1:]:
                        raced_against[racer1].add(racer2)
                        raced_against[racer2].add(racer1)
                
                heats.append(heat_lanes)
            
            # If all racers have raced the required number of times, we're done
            if all(count >= races_per_racer for count in race_counts.values()):
                break
        
        # Check if we've assigned all races
        total_assigned = sum(race_counts.values())
        if total_assigned < total_races:
            # If we couldn't create a perfect schedule, just fill in remaining slots
            remaining_slots = total_races - total_assigned
            eligible_racers = sorted(
                [(r, races_per_racer - race_counts[r]) for r in racer_ids if race_counts[r] < races_per_racer],
                key=lambda x: x[1], reverse=True
            )
            
            while eligible_racers and len(heats) * lanes_per_heat < total_races:
                heat_lanes = {}
                for lane in range(1, lanes_per_heat + 1):
                    if eligible_racers:
                        racer_id, _ = eligible_racers[0]
                        heat_lanes[lane] = racer_id
                        race_counts[racer_id] += 1
                        
                        if race_counts[racer_id] >= races_per_racer:
                            eligible_racers.pop(0)
                        else:
                            eligible_racers[0] = (racer_id, races_per_racer - race_counts[racer_id])
                            eligible_racers.sort(key=lambda x: x[1], reverse=True)
                    else:
                        # Fill empty lanes with racers who already have their quota
                        racers_with_min_races = sorted(
                            [(r, race_counts[r]) for r in racer_ids],
                            key=lambda x: x[1]
                        )
                        if racers_with_min_races:
                            racer_id, _ = racers_with_min_races[0]
                            heat_lanes[lane] = racer_id
                            race_counts[racer_id] += 1
                
                heats.append(heat_lanes)
        
        return heats
    
    def _assign_lanes_by_rank(self, racer_indices: List[int], lanes_per_heat: int) -> Dict[int, int]:
        """
        Assign lanes based on racer ranking.
        Best racers get middle lanes, which are typically faster on most tracks.
        
        Args:
            racer_indices: List of indices into the racers list, sorted by performance
            lanes_per_heat: Number of lanes on the track
            
        Returns:
            Dict mapping lane numbers to racer indices
        """
        lane_assignments = {}
        
        # Sort racers by performance (best first)
        sorted_racers = sorted(racer_indices)
        
        # Assign middle lanes to best racers
        # For a 4-lane track: lane order would be 3, 2, 4, 1 (best to worst)
        # For a 6-lane track: lane order would be 3, 4, 2, 5, 1, 6
        lane_order = []
        
        # Calculate lane preferences (middle lanes first)
        middle = (lanes_per_heat + 1) // 2
        for offset in range(lanes_per_heat):
            if offset % 2 == 0:
                # Even offsets go to the right
                lane = middle + (offset // 2)
                if lane <= lanes_per_heat:
                    lane_order.append(lane)
            else:
                # Odd offsets go to the left
                lane = middle - ((offset + 1) // 2)
                if lane >= 1:
                    lane_order.append(lane)
        
        # Assign racers to lanes by rank
        for i, lane in enumerate(lane_order):
            if i < len(sorted_racers):
                lane_assignments[lane] = sorted_racers[i]
            
        return lane_assignments
    
    async def advance_racers_to_finals(
        self, 
        preliminary_round_id: int, 
        final_round_id: int,
        top_count: int = 4
    ) -> List[Heat]:
        """
        Advance top racers from a preliminary round to a final round.
        
        Args:
            preliminary_round_id: ID of the preliminary round
            final_round_id: ID of the final round
            top_count: Number of top racers to advance
            
        Returns:
            List of created Heat objects
        """
        # Verify rounds exist and are of the correct type
        prelim_round = await self.session.get(Round, preliminary_round_id)
        if not prelim_round or prelim_round.phase != "preliminary":
            raise ValueError(f"Invalid preliminary round ID: {preliminary_round_id}")
            
        final_round = await self.session.get(Round, final_round_id)
        if not final_round or final_round.phase != "final":
            raise ValueError(f"Invalid final round ID: {final_round_id}")
            
        # Ensure the rounds belong to the same division
        if prelim_round.divisionid != final_round.divisionid:
            raise ValueError("Preliminary and final rounds must belong to the same division")
            
        # Check if the final round already has heats
        heat_count_query = select(func.count()).select_from(Heat).where(Heat.roundid == final_round_id)
        heat_count = await self.session.execute(heat_count_query)
        if heat_count.scalar() > 0:
            raise ValueError(f"Final round already has heats")
            
        # Get all heats from preliminary round
        prelim_heats_query = select(Heat.id).where(Heat.roundid == preliminary_round_id)
        prelim_heats_result = await self.session.execute(prelim_heats_query)
        prelim_heat_ids = [heat_id for (heat_id,) in prelim_heats_result]
        
        if not prelim_heat_ids:
            raise ValueError("No heats found in preliminary round")
            
        # Calculate average times for each racer across all heats
        results_query = (
            select(
                RaceResult.racer_id,
                func.avg(RaceResult.time).label("avg_time"),
                func.count(RaceResult.id).label("race_count"),
                Racer.divisionid
            )
            .join(Racer, RaceResult.racer_id == Racer.id)
            .where(
                RaceResult.heat_id.in_(prelim_heat_ids),
                RaceResult.completed == True,
                RaceResult.time.isnot(None)
            )
            .group_by(RaceResult.racer_id, Racer.divisionid)
            .order_by(func.avg(RaceResult.time))
        )
            
        results = await self.session.execute(results_query)
        racers_with_results = [
            {"id": racer_id, "avg_time": avg_time, "race_count": count, "divisionid": divisionid}
            for racer_id, avg_time, count, divisionid in results
        ]
        
        # Get the top performers
        top_racers = racers_with_results[:min(top_count, len(racers_with_results))]
        
        if not top_racers:
            raise ValueError("No racers with results found in preliminary round")
            
        # Create a heat for the final round
        heat = Heat(
            roundid=final_round_id,
            heat=1,
            status="scheduled"
        )
        self.session.add(heat)
        await self.session.flush()
        
        # Get the number of lanes on the track (assuming it's the same as the number of racers)
        lanes_per_heat = len(top_racers)
        
        # Assign racers to lanes based on their ranking
        # Best racers get middle lanes
        racer_indices = list(range(len(top_racers)))
        lane_assignments = self._assign_lanes_by_rank(racer_indices, lanes_per_heat)
        
        for lane, idx in lane_assignments.items():
            racer_id = top_racers[idx]["id"]
            racer_heat = RacerHeat(
                heat_id=heat.id,
                lane=lane,
                racer_id=racer_id
            )
            self.session.add(racer_heat)
            
        await self.session.commit()
        
        return [heat]
    
    async def create_championship_heats(
        self, 
        round_id: int,
        lanes_per_heat: int = 4
    ) -> List[Heat]:
        """
        Create championship heats with the top performers from each division.
        
        Args:
            round_id: ID of the championship round
            lanes_per_heat: Number of lanes on the track
            
        Returns:
            List of created Heat objects
        """
        # Get the championship round
        round_obj = await self.session.get(Round, round_id)
        if not round_obj or round_obj.phase != "championship":
            raise ValueError(f"Invalid championship round ID: {round_id}")
            
        # Check if the championship round already has heats
        heat_count_query = select(func.count()).select_from(Heat).where(Heat.roundid == round_id)
        heat_count = await self.session.execute(heat_count_query)
        if heat_count.scalar() > 0:
            raise ValueError(f"Championship round already has heats")
            
        # Get all divisions
        divisions_query = select(Division).order_by(Division.sort_order)
        divisions_result = await self.session.execute(divisions_query)
        divisions = divisions_result.scalars().all()
        
        top_racers = []
        
        # For each division, find the top performer from their final round
        for division in divisions:
            # Find the final round for this division
            final_query = select(Round).where(
                Round.divisionid == division.id,
                Round.phase == "final"
            )
            final_result = await self.session.execute(final_query)
            final_round = final_result.scalar_one_or_none()
            
            if not final_round:
                continue  # Skip divisions without finals
            
            # Get heats from this final round
            heats_query = select(Heat.id).where(Heat.roundid == final_round.id)
            heats_result = await self.session.execute(heats_query)
            heat_ids = [heat_id for (heat_id,) in heats_result]
            
            if not heat_ids:
                continue  # Skip if no heats
            
            # Get the best performer from this division
            best_result_query = (
                select(
                    RaceResult.racer_id,
                    func.avg(RaceResult.time).label("avg_time"),
                    Racer.firstname,
                    Racer.lastname,
                    Racer.divisionid
                )
                .join(Racer, RaceResult.racer_id == Racer.id)
                .where(
                    RaceResult.heat_id.in_(heat_ids),
                    RaceResult.completed == True,
                    RaceResult.time.isnot(None)
                )
                .group_by(RaceResult.racer_id, Racer.firstname, Racer.lastname, Racer.divisionid)
                .order_by(func.avg(RaceResult.time))
                .limit(1)
            )
            
            best_result = await self.session.execute(best_result_query)
            top_racer = best_result.first()
            
            if top_racer:
                racer_id, avg_time, firstname, lastname, divisionid = top_racer
                top_racers.append({
                    "id": racer_id,
                    "avg_time": avg_time,
                    "name": f"{firstname} {lastname}",
                    "divisionid": divisionid
                })
        
        if not top_racers:
            raise ValueError("No qualifying racers found for championship round")
        
        # Create heats for the championship
        # Sort racers by their average time
        top_racers.sort(key=lambda r: r["avg_time"])
        
        # Determine how many heats we need
        # For championship, we typically want just one heat if possible
        if len(top_racers) <= lanes_per_heat:
            # All champions can race in a single heat
            heat = Heat(
                roundid=round_id,
                heat=1,
                status="scheduled"
            )
            self.session.add(heat)
            await self.session.flush()
            
            # Assign lanes based on ranking (best in middle lanes)
            racer_indices = list(range(len(top_racers)))
            lane_assignments = self._assign_lanes_by_rank(racer_indices, len(top_racers))
            
            for lane, idx in lane_assignments.items():
                racer_id = top_racers[idx]["id"]
                racer_heat = RacerHeat(
                    heat_id=heat.id,
                    lane=lane,
                    racer_id=racer_id
                )
                self.session.add(racer_heat)
            
            await self.session.commit()
            return [heat]
        else:
            # Need multiple heats for championship
            # Implement bracket-style tournament if needed
            # For now, just create one heat with the top performers
            heat = Heat(
                roundid=round_id,
                heat=1,
                status="scheduled"
            )
            self.session.add(heat)
            await self.session.flush()
            
            # Take the top racers that fit in one heat
            top_racers = top_racers[:lanes_per_heat]
            
            # Assign lanes based on ranking
            racer_indices = list(range(len(top_racers)))
            lane_assignments = self._assign_lanes_by_rank(racer_indices, len(top_racers))
            
            for lane, idx in lane_assignments.items():
                racer_id = top_racers[idx]["id"]
                racer_heat = RacerHeat(
                    heat_id=heat.id,
                    lane=lane,
                    racer_id=racer_id
                )
                self.session.add(racer_heat)
            
            await self.session.commit()
            return [heat]
            
    async def get_race_standings(self, division_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Calculate race standings based on all completed heats.
        
        Args:
            division_id: Optional division ID to filter results by division
            
        Returns:
            List of racer standings with average times and race counts
        """
        # Build query to get results for all completed heats
        query = (
            select(
                RaceResult.racer_id,
                func.avg(RaceResult.time).label("avg_time"),
                func.min(RaceResult.time).label("best_time"),
                func.count(RaceResult.id).label("race_count"),
                Racer.firstname,
                Racer.lastname,
                Racer.carno,
                Racer.divisionid,
                Division.name.label("division_name")
            )
            .join(Racer, RaceResult.racer_id == Racer.id)
            .join(Division, Racer.divisionid == Division.id)
            .join(Heat, RaceResult.heat_id == Heat.id)
            .join(Round, Heat.roundid == Round.id)
            .where(
                RaceResult.completed == True,
                RaceResult.time.isnot(None),
                Round.phase == "preliminary"  # Only count preliminary rounds for standings
            )
            .group_by(
                RaceResult.racer_id,
                Racer.firstname,
                Racer.lastname,
                Racer.carno,
                Racer.divisionid,
                Division.name
            )
            .order_by(func.avg(RaceResult.time))
        )
        
        # Apply division filter if provided
        if division_id is not None:
            query = query.filter(Racer.divisionid == division_id)
            
        # Execute query
        result = await self.session.execute(query)
        
        # Build standings data
        standings = []
        for row in result:
            racer_id, avg_time, best_time, race_count, firstname, lastname, carno, divisionid, division_name = row
            
            standings.append({
                "racer_id": racer_id,
                "name": f"{firstname} {lastname}",
                "car_number": carno,
                "divisionid": divisionid,
                "division_name": division_name,
                "avg_time": round(avg_time, 3) if avg_time else None,
                "best_time": round(best_time, 3) if best_time else None,
                "race_count": race_count
            })
            
        # If division_id is provided, sort by average time only
        # If no division_id, group by division and sort within each division
        if division_id is not None:
            # Already sorted by avg_time in the query
            pass
        else:
            # Group by division and sort within each division
            standings_by_division = {}
            for entry in standings:
                div_id = entry["divisionid"]
                if div_id not in standings_by_division:
                    standings_by_division[div_id] = []
                standings_by_division[div_id].append(entry)
                
            # Rebuild standings ordered by division
            standings = []
            divisions_query = select(Division).order_by(Division.sort_order)
            divisions_result = await self.session.execute(divisions_query)
            divisions = divisions_result.scalars().all()
            
            for division in divisions:
                if division.id in standings_by_division:
                    # Add racers from this division (already sorted by avg_time)
                    standings.extend(standings_by_division[division.id])
        
        return standings