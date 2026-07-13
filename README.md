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

### ➡️ [Part 2: Business Logic and API Endpoints](./part2/hbnb/README.md)
This phase transitions the system from design to active code, focusing on the core business logic and presentation layers. Key implementations include:
* **Presentation Layer (API):** RESTful API endpoints built with **Flask** and **Flask-RESTx**, utilizing Namespaces for structured routing.
* **Business Logic Layer:** Core domain models implementing strict attribute validation (e.g., latitude/longitude bounds) and entity relationship handling (Nested Serialization).
* **Facade Pattern:** A centralized `HBnBFacade` service orchestrating secure interactions between the layers.

*👉 **[Click here to explore the Part 2 Codebase](./part2/hbnb/README.md)***.
