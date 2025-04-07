# derby_director/main.py
"""
Main entry point for Derby Director API
"""

import os
from typing import List

from litestar import Litestar, get, Response
from litestar.config.cors import CORSConfig
from litestar.openapi import OpenAPIConfig
from litestar.openapi.plugins import ScalarRenderPlugin
from litestar.stores.memory import MemoryStore
from advanced_alchemy.extensions.litestar import SQLAlchemyPlugin, SQLAlchemyAsyncConfig

from backend.config import (
    DATABASE_URL, APP_SETTINGS, DEBUG, CORS_ORIGINS
)
from backend.api.models import Base
from backend.api.controllers import (
    AuthController, RacerController, DivisionController,
    HeatController, ResultController, RoundController
)
from backend.api.middleware.auth import JWTAuthMiddleware


def get_controllers() -> List:
    """Get all controllers for the application"""
    return [
        AuthController,
        RacerController,
        DivisionController,
        HeatController,
        ResultController,
        RoundController
    ]


def create_app() -> Litestar:
    """Create and configure the Litestar application"""
    
    # Database configuration
    sqlalchemy_config = SQLAlchemyAsyncConfig(
        connection_string=DATABASE_URL,
        metadata=Base.metadata,
        session_dependency_key="session"
    )
    sqlalchemy_plugin = SQLAlchemyPlugin(
        config=sqlalchemy_config
    )
    
    # CORS configuration
    cors_config = CORSConfig(
        allow_origins=CORS_ORIGINS,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type"],
        allow_credentials=True
    )
    
    # OpenAPI configuration for API documentation
    openapi_config = OpenAPIConfig(
        title=APP_SETTINGS["title"],
        version=APP_SETTINGS["version"],
        summary="API for Derby Director race management system",
        description=(
            "Derby Director API provides endpoints for managing pinewood derby races, "
            "including racers, heats, results, and timer interfaces."
        ),
        use_handler_docstrings=True,
        render_plugins=[ScalarRenderPlugin()]
    )
    
    # Create the application
    app = Litestar(
        route_handlers=get_controllers(),
        plugins=[sqlalchemy_plugin],
        cors_config=cors_config,
        openapi_config=openapi_config,
        #middleware=[JWTAuthMiddleware],
        debug=DEBUG,
        state={"store": MemoryStore()}
    )
    
    return app


# Create the application instance
app = create_app()


def run_app() -> None:
    """Run the application (used by Poetry script)"""
    import uvicorn
    
    # Get port from environment or use default
    port = int(os.getenv("PORT", "8000"))
    
    # Run the server
    uvicorn.run(
        "derby_director.main:app",
        host="0.0.0.0",
        port=port,
        reload=DEBUG
    )


# Run the application if executed directly
if __name__ == "__main__":
    run_app()