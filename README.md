# HBnB Evolution 🚀

**Project Team:** Alanoud Aloraydi, Leen Algraawi, Reema Alshahrani

## Project Description
HBnB Evolution is a simplified version of an AirBnB-like application. The overall system is designed to allow users to perform the following primary operations:

* **User Management:** Users can register, update their profiles, and be identified as either regular users or administrators.
* **Place Management:** Users can list properties (places) they own, specifying details such as name, description, price, location (latitude and longitude), and a list of amenities.
* **Review Management:** Users can leave reviews for places they have visited, including a rating.

---

## 📂 Project Documentation

To ensure a clean and organized repository, the technical architecture and design blueprints are documented in the project phases below.

### ➡️ [Part 1: Technical Documentation](./part1/README.md)
This phase covers the foundational software architecture and system design. Key sections include:
* **High-Level Architecture:** Three-tier layered architecture and Facade pattern implementation.
* **Business Logic Layer:** Detailed UML Class Diagrams for core entities (`User`, `Place`, `Review`, `Amenity`).
* **API Interaction Flow:** Comprehensive Sequence Diagrams with validation, error handling, and criteria-based filtering.

*👉 **[Click here to read the full Part 1 Technical Documentation](./part1/README.md)***.

### ➡️ [Part 2: Business Logic and API Endpoints](./part2/README.md)
This phase transitions the system from design to active code, focusing on the core business logic and presentation layers. Key implementations include:
* **Presentation Layer (API):** RESTful API endpoints built with **Flask** and **Flask-RESTx**, utilizing Namespaces for structured routing.
* **Business Logic Layer:** Core domain models implementing strict attribute validation (e.g., latitude/longitude bounds) and entity relationship handling (Nested Serialization).
* **Facade Pattern:** A centralized `HBnBFacade` service orchestrating secure interactions between the layers.

*👉 **[Click here to explore the Part 2 Codebase](./part2/README.md)***.

### ➡️ [Part 3: Authentication and Database Integration](./part3/README.md)
This phase secures the backend and replaces in-memory storage with a persistent database. Key implementations include:
* **Authentication:** JWT-based login (**Flask-JWT-Extended**) with bcrypt-hashed passwords, never returned by the API.
* **Authorization:** Role-based access control — ownership checks on places and reviews, admin bypass, and admin-only user/amenity management.
* **Persistence:** In-memory repositories replaced by **SQLAlchemy**-backed SQLite storage, plus raw SQL scripts and a Mermaid ER diagram of the schema.

*👉 **[Click here to explore the Part 3 Codebase](./part3/README.md)***.

### ➡️ [Part 4: Simple Web Client](./part4/README.md)
This phase adds a browser-based client on top of the Part 3 API, built with plain HTML5, CSS3 and JavaScript ES6 — no frameworks, no build step. Key implementations include:
* **Client Pages:** A place list with a price filter, a place detail view with amenities and reviews, a login form, and an add-review form.
* **API Integration:** `fetch`-based calls to `/api/v1/...` with a JWT stored in a cookie after login and sent as a `Bearer` token on every subsequent request.
* **Bundled API:** The Part 3 Flask API is included alongside the client so the two can run together as a full-stack demo.

*👉 **[Click here to explore the Part 4 Codebase](./part4/README.md)***.

---

## ▶️ Running the Project (Part 4)

Part 4 needs two servers running at the same time: the Flask API and a static file server for the client.

**1. Start the API**
```bash
cd part4
python -m venv venv && source venv/bin/activate   # if not already set up
pip install -r requirements.txt
python run.py
```
This serves the API on `http://localhost:5000` and automatically creates `instance/development.db` with a seeded admin account (`admin@hbnb.io` / `admin1234`) on first run.

**2. Start the client (in a second terminal)**
```bash
cd part4/base_files
python -m http.server 8000
```

**3. Open the client**

Open `http://localhost:8000/index.html` in your browser. The client communicates with the API at `http://localhost:5000`, and CORS is enabled on the API to allow this cross-origin connection.