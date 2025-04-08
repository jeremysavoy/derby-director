# backend/migrations/init_db.py
"""
Initialize the database with schema and seed data
"""

import asyncio
import logging
import os
import importlib.metadata

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def run_alembic_migrations():
    """Run Alembic migrations to create the schema"""
    try:
        from alembic.config import Config
        from alembic import command
        import asyncio
        
        # Get the directory of this script
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        # Create alembic.ini path
        alembic_ini = os.path.join(os.path.dirname(base_dir), "alembic.ini")
        
        if not os.path.exists(alembic_ini):
            logger.error(f"Could not find alembic.ini at {alembic_ini}")
            logger.error("Please run this script from the project root directory")
            return False
        
        # Load configuration and run migrations
        alembic_cfg = Config(alembic_ini)
        
        # Since we can't await command.upgrade directly (it's synchronous),
        # we need to run it in a separate thread/process to avoid blocking
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, lambda: command.upgrade(alembic_cfg, "head"))
        
        logger.info("Database schema created successfully!")
        return True
        
    except ImportError:
        logger.error("Alembic is not installed. Please install using: poetry add alembic")
        return False
    except Exception as e:
        logger.error(f"Error running migrations: {e}")
        return False


async def run_seed_data():
    """Run seed data script to populate the database"""
    try:
        from backend.migrations.seed_data import seed_database
        
        await seed_database()
        return True
        
    except ImportError:
        logger.error("Could not import seed_database function")
        return False
    except Exception as e:
        logger.error(f"Error seeding database: {e}")
        return False


async def main():
    """Main entry point"""
    logger.info("Initializing Derby Director database...")
    
    # Run migrations
    migrations_success = await run_alembic_migrations()
    if not migrations_success:
        logger.error("Failed to apply migrations. Exiting.")
        return
    
    # Run seed data
    seed_success = await run_seed_data()
    if not seed_success:
        logger.error("Failed to seed database. You may need to seed manually.")
        return
    
    logger.info("Database initialization complete!")
    logger.info("You can now start the application with: poetry run start")


if __name__ == "__main__":
    asyncio.run(main())