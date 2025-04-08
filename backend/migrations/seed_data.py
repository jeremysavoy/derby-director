# backend/migrations/seed_data.py
"""
Script to seed the database with initial data for testing
"""

import asyncio
import logging
import json
from datetime import datetime, timedelta
import hashlib
import random

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import text

from backend.config import DATABASE_URL
from backend.api.models import (
    Division, Rank, Racer, Round, Heat, RacerHeat, 
    Settings, TimerConfiguration
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Sample data
DIVISIONS = [
    {"name": "Lions", "sort_order": 1},
    {"name": "Tigers", "sort_order": 2},
    {"name": "Wolves", "sort_order": 3},
    {"name": "Bears", "sort_order": 4},
    {"name": "Webelos", "sort_order": 5},
    {"name": "Arrow of Light", "sort_order": 6},
    {"name": "Open Division", "sort_order": 7}
]

RANKS = [
    {"name": "Lion", "sort_order": 1},
    {"name": "Tiger", "sort_order": 2},
    {"name": "Wolf", "sort_order": 3},
    {"name": "Bear", "sort_order": 4},
    {"name": "Webelos", "sort_order": 5},
    {"name": "Arrow of Light", "sort_order": 6}
]

# Names for generating sample racers
FIRST_NAMES = [
    "James", "John", "Robert", "Michael", "William", "David", "Richard", "Joseph",
    "Thomas", "Charles", "Daniel", "Matthew", "Anthony", "Mark", "Donald", "Steven",
    "Andrew", "Paul", "Joshua", "Kenneth", "Kevin", "Brian", "George", "Timothy",
    "Emma", "Olivia", "Ava", "Isabella", "Sophia", "Charlotte", "Mia", "Amelia",
    "Harper", "Evelyn", "Abigail", "Emily", "Elizabeth", "Sofia", "Avery", "Ella",
    "Scarlett", "Grace", "Victoria", "Riley", "Aria", "Lily", "Aubrey", "Zoey"
]

LAST_NAMES = [
    "Smith", "Johnson", "Williams", "Jones", "Brown", "Davis", "Miller", "Wilson",
    "Moore", "Taylor", "Anderson", "Thomas", "Jackson", "White", "Harris", "Martin",
    "Thompson", "Garcia", "Martinez", "Robinson", "Clark", "Rodriguez", "Lewis", "Lee",
    "Walker", "Hall", "Allen", "Young", "Hernandez", "King", "Wright", "Lopez", "Hill",
    "Scott", "Green", "Adams", "Baker", "Gonzalez", "Nelson", "Carter", "Mitchell",
    "Perez", "Roberts", "Turner", "Phillips", "Campbell", "Parker", "Evans", "Edwards"
]

CAR_ADJECTIVES = [
    "Fast", "Sleek", "Lightning", "Thunder", "Rocket", "Speedy", "Blazing", "Rapid",
    "Swift", "Racing", "Fiery", "Turbo", "Zoom", "Quick", "Flash", "Bolt", "Speed",
    "Streak", "Sonic", "Velocity", "Nitro", "Bullet", "Jet", "Comet", "Star", "Blaze"
]

CAR_NOUNS = [
    "Racer", "Runner", "Bullet", "Arrow", "Bolt", "Streak", "Flash", "Dash", "Rocket",
    "Lightning", "Thunder", "Comet", "Blaze", "Fury", "Storm", "Wind", "Cyclone",
    "Tornado", "Hurricane", "Phoenix", "Dragon", "Shark", "Tiger", "Eagle", "Falcon"
]


async def seed_database():
    """Seed the database with initial data"""
    engine = create_async_engine(DATABASE_URL)
    async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    
    async with async_session() as session:
        # Check if data already exists
        result = await session.execute(text("SELECT COUNT(*) FROM divisions"))
        count = result.scalar()
        
        if count > 0:
            logger.info("Database already has data, skipping seed.")
            return
        
        logger.info("Seeding database with initial data...")
        
        # Add divisions
        division_objects = {}
        for division_data in DIVISIONS:
            dvsn = Division(**division_data)
            session.add(dvsn)
            await session.flush()
            division_objects[dvsn.name] = dvsn
        
        # Add ranks
        rank_objects = {}
        for rank_data in RANKS:
            rank = Rank(**rank_data)
            session.add(rank)
            await session.flush()
            rank_objects[rank.name] = rank
        
        # Add racers (5-10 per division)
        all_racers = []
        car_number = 1
        
        for division_name, dvsn in division_objects.items():
            # Determine which rank to use for this division
            rank = None
            if division_name == "Lions":
                rank = rank_objects["Lion"]
            elif division_name == "Tigers":
                rank = rank_objects["Tiger"]
            elif division_name == "Wolves":
                rank = rank_objects["Wolf"]
            elif division_name == "Bears":
                rank = rank_objects["Bear"]
            elif division_name == "Webelos":
                rank = rank_objects["Webelos"]
            elif division_name == "Arrow of Light":
                rank = rank_objects["Arrow of Light"]
            
            # Generate random number of racers for this division
            num_racers = random.randint(5, 10)
            
            for _ in range(num_racers):
                firstname = random.choice(FIRST_NAMES)
                lastname = random.choice(LAST_NAMES)
                carno = str(car_number)
                car_number += 1
                
                # Generate a fun car name
                carname = f"{random.choice(CAR_ADJECTIVES)} {random.choice(CAR_NOUNS)}"
                
                # Create racer
                racer = Racer(
                    firstname=firstname,
                    lastname=lastname,
                    divisionid=dvsn.id,
                    rankid=rank.id if rank else None,
                    carno=carno,
                    carname=carname,
                    exclude=False,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                session.add(racer)
                all_racers.append(racer)
        
        await session.flush()
        
        # Add rounds - one per division plus finals
        round_objects = []
        for division_name, dvsn in division_objects.items():
            prelim_round = Round(
                name=f"{division_name} Preliminary",
                divisionid=dvsn.id,
                roundno=1,
                phase="normal",
                charttype="roster"
            )
            session.add(prelim_round)
            round_objects.append(prelim_round)
        
        # Add a finals round
        finals_round = Round(
            name="Finals",
            divisionid=None,  # All divisions
            roundno=2,
            phase="final",
            charttype="roster"
        )
        session.add(finals_round)
        round_objects.append(finals_round)
        
        await session.flush()
        
        # Create heats for the first round
        for round_obj in round_objects:
            if round_obj.name == "Finals":
                continue  # Skip finals for now
                
            # Get racers for this division
            division_racers = [r for r in all_racers if r.divisionid == round_obj.divisionid]
            
            # Create heats for these racers (assuming 4-lane track)
            lane_count = 4
            heat_number = 1
            
            # Simple round-robin assignment (not optimal but good for demo)
            for i in range(0, len(division_racers), lane_count):
                heat = Heat(
                    roundid=round_obj.id,
                    heat=heat_number,
                    status="scheduled"
                )
                session.add(heat)
                await session.flush()
                
                # Assign racers to lanes
                for lane in range(1, lane_count + 1):
                    racer_index = i + lane - 1
                    if racer_index < len(division_racers):
                        racer = division_racers[racer_index]
                        racer_heat = RacerHeat(
                            heat_id=heat.id,
                            lane=lane,
                            racer_id=racer.id
                        )
                        session.add(racer_heat)
                
                heat_number += 1
        
        # Add settings
        settings = [
            Settings(key="admin_password", value="doyourbest"),
            Settings(key="event_name", value="Pinewood Derby"),
            Settings(key="lanes", value="4"),
            Settings(key="organization", value="Pack 123")
        ]
        for setting in settings:
            session.add(setting)
        
        # Add timer configuration
        timer_config = TimerConfiguration(
            timer_type="smartline",
            connection_type="serial",
            connection_details=json.dumps({
                "port": "COM1",
                "baudrate": 9600
            }),
            lanes=4,
            is_active=1
        )
        session.add(timer_config)
        
        await session.commit()
        logger.info("Database seeded successfully!")


async def main():
    """Main entry point"""
    try:
        await seed_database()
    except Exception as e:
        logger.error(f"Error seeding database: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())