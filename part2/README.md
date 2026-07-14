# HBnB - Holberton BnB

A modular, layered web application implementing the core business logic and API for an AirBnB-style platform. This part of the project focuses on setting up the project structure, business logic classes, and API endpoints using the **Facade design pattern**, with an in-memory persistence layer that will later be replaced by a database-backed solution.

## Project Overview

The HBnB application is organized into three main layers:

- **Presentation Layer** (`app/api/`) — Exposes the RESTful API endpoints (via Flask-RESTx) that clients use to interact with the application. Endpoints are versioned (`v1/`) and cover users, places, reviews, and amenities.
- **Business Logic Layer** (`app/models/`) — Contains the core domain classes (`User`, `Place`, `Review`, `Amenity`) that define the entities and rules of the application.
- **Persistence Layer** (`app/persistence/`) — Handles storage and retrieval of objects. Currently implemented as an in-memory repository; will be replaced with a SQLAlchemy-backed database repository in a later part of the project.

Communication between these layers is managed through the **Facade pattern**, implemented in `app/services/facade.py`. The `HBnBFacade` class acts as a single point of contact between the API layer and the underlying business logic and persistence layers, keeping the codebase decoupled and easier to maintain.

## Project Structure

```
hbnb/
├── app/
│   ├── __init__.py          # Flask application factory
│   ├── api/
│   │   ├── __init__.py
│   │   ├── v1/
│   │       ├── __init__.py
│   │       ├── users.py     # User endpoints
│   │       ├── places.py    # Place endpoints
│   │       ├── reviews.py   # Review endpoints
│   │       ├── amenities.py # Amenity endpoints
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py          # User business logic class
│   │   ├── place.py         # Place business logic class
│   │   ├── review.py        # Review business logic class
│   │   ├── amenity.py       # Amenity business logic class
│   ├── services/
│   │   ├── __init__.py      # Facade singleton instance
│   │   ├── facade.py        # HBnBFacade class
│   ├── persistence/
│       ├── __init__.py
│       ├── repository.py    # Repository interface + in-memory implementation
├── run.py                   # Application entry point
├── config.py                # Environment/application configuration
├── requirements.txt         # Python dependencies
├── README.md                # Project documentation
```

### Directory & File Overview

| Path | Purpose |
|---|---|
| `app/` | Core application package |
| `app/api/v1/` | Version 1 of the REST API endpoints |
| `app/models/` | Business logic entities (User, Place, Review, Amenity) |
| `app/services/` | Facade pattern implementation — mediates between API and persistence |
| `app/persistence/` | Storage layer — currently an in-memory repository, later a database repository |
| `run.py` | Entry point used to launch the Flask application |
| `config.py` | Application configuration and environment settings |
| `requirements.txt` | List of required Python packages |

## Design Patterns

- **Facade Pattern** — `HBnBFacade` provides a simplified, unified interface to the business logic and persistence layers, so the API layer never has to interact with repositories directly.
- **Repository Pattern** — The `Repository` abstract base class defines a consistent storage interface (`add`, `get`, `get_all`, `update`, `delete`, `get_by_attribute`). The `InMemoryRepository` is the current implementation and will later be swapped for a SQLAlchemy-based repository without changing the rest of the codebase.

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd hbnb
   ```

2. (Recommended) Create and activate a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Running the Application

Start the Flask application with:

```bash
python run.py
```

The application will run in debug mode. At this stage, the API documentation (Swagger UI) is available at `/api/v1/`, though functional routes will be added in later parts of the project.

## Requirements

- Python 3.x
- Flask
- Flask-RESTx

## Status

This part of the project establishes the foundational project structure, the Facade pattern, and the in-memory repository. Business logic validation, API endpoint implementation, and full CRUD operations will be added in subsequent parts. The in-memory persistence layer will eventually be replaced with a database-backed implementation using SQLAlchemy.

## Author

*Alanoud Aloraydi, Leen Algraawi, Reema Alshahrani.*