# HBnB Evolution - Part 1: Technical Documentation

## Project Overview
This repository contains **Part 1** of the HBnB Evolution project. This initial phase is dedicated entirely to designing the software architecture, conceptualizing the package structure, and creating the technical documentation required before implementation.

## Architectural Layers & Package Structure
The system is designed following the **Layered Architecture Pattern** to ensure a strict separation of concerns. It is structured into three main packages:

- **Presentation Layer (Services / API):** Defines the entry points of the application, handles incoming HTTP requests, and returns the appropriate responses to the client.
- **Business Logic Layer (Models):** Contains the core domain models (User, Place, Review, Amenity) and enforces the business rules and logic of the application.
- **Persistence Layer:** Manages data storage, retrieval, and structural abstraction, ensuring that data is safely preserved independently of the business logic.

## Technical Deliverables
This phase includes the following architectural diagrams:
- **High-Level Architecture Diagram:** Visualizes the package structure and the data flow between layers.
- **Detailed Class Diagram:** Maps out the business logic entities, their attributes, methods, and relationships in compliance with SOLID principles.
- **Sequence Diagrams:** Illustrates step-by-step interactions across layers for core operations (e.g., User Registration, Place Creation).
