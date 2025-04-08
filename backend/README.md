# Derby Director

A modern race management system for pinewood derby events, built with Python, Litestar, and Vue.js.

## Features

- Complete racer registration and management
- Race scheduling and heat organization
- Live race timing with hardware integration
- Results tracking and reporting
- Award certificate generation
- Modern, responsive user interface

## Installation

Derby Director uses Poetry for dependency management.

### Prerequisites

- Python 3.9+
- Poetry 1.4+

### Setup

1. Clone the repository:

```bash
git clone https://github.com/yourusername/derby-director.git
cd derby-director
```

2. Install dependencies:

```bash
poetry install
```

If you need MySQL support:

```bash
poetry install -E mysql
```

3. Initialize the database:

```bash
poetry run python -m backend.migrations.init_db
```

## Development

### Running the backend server

```bash
poetry run uvicorn backend.main:app --reload
```

The API will be available at http://localhost:8000 with API documentation at http://localhost:8000/docs

### Running tests

```bash
poetry run pytest
```

## Project Structure

```
backend/
├── api/                    # API package
│   ├── controllers/        # API route handlers
│   ├── models/             # Database models
│   ├── schemas/            # Pydantic schemas
│   ├── services/           # Business logic services
│   │   └── timer/          # Timer integration
│   └── middleware/         # Authentication middleware
├── migrations/             # Database migrations
├── tests/                  # Test suite
├── config.py               # Configuration
└── main.py                 # Application entry point
```

## Timer Hardware Support

Derby Director is designed to work with various timer hardware systems:

- SmartLine Timer
- FastTrack Timer
- Support for more timers can be added by implementing the TimerInterface

## License

MIT