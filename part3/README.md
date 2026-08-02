# HBnB - Holberton BnB

A modular, layered web application implementing the core business logic and API for an AirBnB-style platform. This part uses the **Facade design pattern** with SQLAlchemy-backed persistence.

## Project Overview

The HBnB application is organized into three main layers:

- **Presentation Layer** (`app/api/`) — Exposes the RESTful API endpoints (via Flask-RESTx) that clients use to interact with the application. Endpoints are versioned (`v1/`) and cover users, places, reviews, and amenities.
- **Business Logic Layer** (`app/models/`) — Contains the core domain classes (`User`, `Place`, `Review`, `Amenity`) that define the entities and rules of the application.
- **Persistence Layer** (`app/persistence/`) — Handles storage and retrieval through SQLAlchemy repositories.

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
│       ├── repository.py    # Repository interface + SQLAlchemy implementation
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
| `app/persistence/` | SQLAlchemy-backed storage layer |
| `run.py` | Entry point used to launch the Flask application |
| `config.py` | Application configuration and environment settings |
| `requirements.txt` | List of required Python packages |

## Design Patterns

- **Facade Pattern** — `HBnBFacade` provides a simplified, unified interface to the business logic and persistence layers, so the API layer never has to interact with repositories directly.
- **Repository Pattern** — The `Repository` contract is implemented by `SQLAlchemyRepository` for mapped persistence.

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
- Flask-Bcrypt
- Flask-SQLAlchemy

## Status

This part establishes the application factory, mapped domain models, SQLAlchemy repositories, business validation, and CRUD API behavior.

## Task 9: Raw SQLite Scripts

Task 9 demonstrates database creation and CRUD operations independently of
SQLAlchemy and `db.create_all()`. The SQLite scripts are located in `sql/`:

- `schema.sql` creates the five Task 9 tables and their constraints.
- `seed.sql` inserts the fixed administrator and three required Amenities.
- `crud_test.sql` exercises direct SQL CRUD operations and rolls them back.

The administrator ID is fixed by the assignment. Amenity IDs were generated
once as UUID4 values, and the CRUD demonstration uses separate fixed UUID4
values for repeatable testing. New application records must supply their own
UUID4 identifiers. The administrator password column contains only a bcrypt
hash generated using Flask-Bcrypt; the plaintext value is not stored in the SQL
scripts or this documentation.

From the `part3` directory, create and seed a fresh local database with:

```powershell
Remove-Item -LiteralPath task9_test.db -ErrorAction SilentlyContinue
python -c "import sqlite3; conn=sqlite3.connect('task9_test.db'); conn.executescript(open('sql/schema.sql', encoding='utf-8').read()); conn.executescript(open('sql/seed.sql', encoding='utf-8').read()); conn.close()"
```

Inspect the seeded rows without exposing password data:

```powershell
python -c "import sqlite3; conn=sqlite3.connect('task9_test.db'); print(conn.execute('SELECT id, first_name, last_name, email, is_admin FROM users').fetchall()); print(conn.execute('SELECT id, name FROM amenities ORDER BY name').fetchall()); conn.close()"
```

Run the rollback-only CRUD demonstration:

```powershell
python -c "import sqlite3; conn=sqlite3.connect('task9_test.db'); conn.executescript(open('sql/crud_test.sql', encoding='utf-8').read()); conn.close()"
```

Remove the manual database afterward:

```powershell
Remove-Item -LiteralPath task9_test.db
```

Run the focused Task 9 tests and complete Part 3 suite with:

```powershell
python -m unittest tests.test_sql_scripts -v
python -m unittest discover -s tests -v
```

The final regression totals are 53 Part 2 tests and 76 Part 3 tests, for 129
unique tests overall. The 18 focused Task 9 tests are included in the 76-test
Part 3 suite and are not counted a second time.

The raw Task 9 schema follows the assignment's explicit SQL definitions. It is
intentionally not identical to the current ORM mapping, which also defines
timestamps, shorter strings, an Amenity description, non-null fields, Python-side
defaults, and ORM relationship cascades.

## Task 10: Database Diagram

Task 10 documents the Task 9 raw SQL schema as an editable Mermaid ER diagram.
See the [diagram documentation](ER_DIAGRAM.md), the
[Mermaid source](diagrams/hbnb_er_diagram.mmd), and the exported SVG below.
GitHub can render the Mermaid source in `ER_DIAGRAM.md` directly.

![HBnB database ER diagram](diagrams/hbnb_er_diagram.svg)

Regenerate and validate the SVG from the repository root with the official
Mermaid CLI without creating a local JavaScript project:

```powershell
npx -y @mermaid-js/mermaid-cli -i part3/diagrams/hbnb_er_diagram.mmd -o part3/diagrams/hbnb_er_diagram.svg
```

On Windows PowerShell, if the execution policy blocks `npx.ps1`, use the
`npx.cmd` launcher instead:

```powershell
npx.cmd -y @mermaid-js/mermaid-cli -i part3\diagrams\hbnb_er_diagram.mmd -o part3\diagrams\hbnb_er_diagram.svg
```

If Mermaid CLI cannot download or locate Chrome, the tested Windows fallback is
to provide the Chrome executable explicitly and skip its download:

```powershell
$env:PUPPETEER_SKIP_DOWNLOAD='true'
$env:PUPPETEER_EXECUTABLE_PATH='C:\Program Files\Google\Chrome\Application\chrome.exe'
npx.cmd -y @mermaid-js/mermaid-cli -i part3\diagrams\hbnb_er_diagram.mmd -o part3\diagrams\hbnb_er_diagram.svg
```

The installed Chrome path may differ by system.

If Mermaid CLI is unavailable, copy `part3/diagrams/hbnb_er_diagram.mmd` into
the official Mermaid Live Editor, validate it there, and export the result to
`part3/diagrams/hbnb_er_diagram.svg`.

Reservation or Booking would be a future conceptual extension; neither entity
is part of the implemented Task 9 schema or the authoritative diagram.

## Author

*Alanoud Aloraydi, Leen Algraawi, Reema Alshahrani.*
