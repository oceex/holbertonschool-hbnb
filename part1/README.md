# HBnB Evolution - Part 1: Technical Documentation

**Team:** Alanoud Aloraydi, Leen Algraawi, Reema Alshahrani  
**Project:** HBnB Evolution (Part 1)  

---

## 1. Project Overview
This repository contains Part 1 of the HBnB Evolution project. This initial phase is dedicated entirely to designing the software architecture, conceptualizing the package structure, and creating the technical documentation required before implementation.

---

## 2. High-Level Architecture & Package Diagram
The HBnB Evolution system utilizes a **three-tier layered architecture** to ensure a clean separation of concerns and system modularity.


```mermaid
classDiagram
    class PresentationLayer {
        <<Package>>
        +API_Endpoints
        +Services
    }

    class HBnBFacade {
        <<Facade / Interface>>
        +orchestrate_requests()
    }

    class BusinessEntities {
        <<Package>>
        +User
        +Place
        +Review
        +Amenity
    }

    class PersistenceLayer {
        <<Package>>
        +DatabaseAccess
    }

    %% Relationships
    PresentationLayer ..> HBnBFacade : Calls
    HBnBFacade ..> BusinessEntities : Coordinates Access
    HBnBFacade ..> PersistenceLayer : Database Operations
```
### I. Presentation Layer
Acts as the system’s interface, managing all external communication.

Responsibility: Handles HTTP requests, validates incoming data, and formats outgoing JSON responses with appropriate HTTP status codes.

### II. Business Logic Layer
Serves as the core processing engine, housing all application rules and domain entities (User, Place, Review, Amenity).

Responsibility: Orchestrates system behavior independent of the interface or database. It is accessed exclusively via the HBnBFacade, which acts as a mediator providing a unified entry point and coordinating all access to the business entities.

### III. Persistence Layer
Manages the interaction between the application and the data storage system.

Responsibility: Executes all read/write operations. By abstracting the storage mechanism, it allows the system to switch storage technologies without affecting the upper layers.

---

## 3. Business Logic Layer
This layer defines the core entities of the application, isolating pure domain state and behavior from the underlying infrastructure, API routes, or persistence frameworks.

### I. Detailed Class Diagram
```mermaid
classDiagram
    class BaseModel {
        <<abstract>>
        +UUID4 id
        +DateTime created_at
        +DateTime updated_at
        +create(data: dict): BaseModel
        +update(data: dict): void
        +delete(): boolean
        +list(): List~BaseModel~
    }

    class User {
        +String first_name
        +String last_name
        +String email
        -String password_hash
        +Boolean is_admin
        +register(data: dict): User
        +verify_password(password: String): Boolean
        +update_profile(data: dict): void
        +delete(): boolean
        +list(): List~User~
    }

    class Place {
        +String title
        +String description
        +Float price
        +Float latitude
        +Float longitude
        #UUID4 owner_id
        +add_review(review: Review): void
        +add_amenity(amenity: Amenity): void
        +create(data: dict): Place
        +update(data: dict): void
        +delete(): boolean
        +list(): List~Place~
    }

    class Review {
        +String comment
        +Integer rating
        #UUID4 user_id
        #UUID4 place_id
        +validate_rating(rating: Integer): Boolean
        +create(data: dict): Review
        +update(data: dict): void
        +delete(): boolean
        +list(place_id: UUID4): List~Review~
    }

    class Amenity {
        +String name
        +String description
        +create(data: dict): Amenity
        +update(data: dict): void
        +delete(): boolean
        +list(): List~Amenity~
    }

    %% Inheritance
    BaseModel <|-- User : inherits
    BaseModel <|-- Place : inherits
    BaseModel <|-- Review : inherits
    BaseModel <|-- Amenity : inherits

    %% Associations
    User "1" --> "0..*" Place : owns
    User "1" --> "0..*" Review : authors
    Place "1" *-- "0..*" Review : receives
    Place "0..*" --> "0..*" Amenity : has
```
### II. Detailed Entity Analysis & Architectural Roles

**BaseModel:** Provides core identity framework using UUID4, created_at, and updated_at timestamps.

**User Entity:** Manages actors and profiles. It secures credentials via password_hash and handles domain behaviors like verify_password().

**Place Entity:** The core property node (specs, price, owner_id). It actively manages state via methods like add_review().

**Review Entity:** Tracks customer feedback. It enforces rules using methods like validate_rating().


**Amenity Entity:** A global feature catalog linked across properties to enrich details.

### III. Advanced Relationship Dynamics & Multiplicity

**Inheritance:** All entities inherit BaseModel to prevent code duplication.


**User to Place (1 to 0..*):** A user can host multiple listings.


**User to Review (1 to 0..*):** Unidirectional mapping ensuring every review is tied to a valid user.


**Place to Review (1 to 0.. Composition):* ** Cascading deletion (*--); reviews are destroyed if the target Place is deleted.


**Place to Amenity (0.. to 0..*):* ** Many-to-many mapping for flexible utility catalogs.

### IV. Design Decisions (SOLID)

**SRP (Single Responsibility Principle):** Each entity manages only its specific domain (e.g., Place for property specs, Review for metrics).


**OCP (Open/Closed Principle):** Easily extensible for future models without breaking existing code.


### Encapsulation: Protects sensitive data (like password_hash) and internal states from external interference.
--- 

## 4. API Interaction Flow (Sequence Diagrams)
The following diagrams illustrate the Request Lifecycle across the application's layers for core operations, including both successful executions (Happy Paths) and failure scenarios (Error Flows) using alt blocks.

**Business Logic Layer:** Encapsulates the core domain models, executes validations, and enforces business constraints.

**Persistence Layer:** Manages data storage and retrieval abstractions.

**Design Decisions & Rationale:** We implemented the Facade Pattern (HBnBFacade) to act as a unified interface between the Presentation and Business layers. This decision decouples the API from the complex internal subsystem logic and explicitly handles validation errors before they reach the database.

### I. User Registration
Flow Explanation: The client sends a JSON payload. The HBnBFacade first checks if the email already exists to prevent duplicates. If valid, it hashes the password for security, instantiates the User object, and delegates storage to the DB. If validation fails, it immediately returns a 400 or 409 error.

```mermaid
sequenceDiagram
    autonumber
    participant Client
    participant API as Presentation Layer
    participant Facade as Business Logic (Facade)
    participant DB as Persistence Layer

    Client->>API: POST /users (JSON Payload)
    API->>Facade: register_user(data)
    activate Facade
    Facade->>DB: check_email_exists(data.email)
    
    alt Email Already Exists
        DB-->>Facade: True
        Facade-->>API: Raise ConflictError
        API-->>Client: 409 Conflict (Email in use)
    else Valid Data
        DB-->>Facade: False
        Facade->>Facade: Validate Inputs & Hash Password
        Facade->>Facade: Instantiate User_Object
        Facade->>DB: save(User_Object)
        activate DB
        DB-->>Facade: Confirm Save
        deactivate DB
        Facade-->>API: Return User_Object
        API-->>Client: 201 Created (User Data without Password)
    end
    deactivate Facade
```
### II. Place Creation
Flow Explanation: Place creation demands strict validation of fields (price, latitude, longitude, amenities) and foreign key integrity. The Facade ensures the owner_id correlates to a valid existing User. If any validation fails or the owner is missing, the flow aborts with an appropriate HTTP error.

```mermaid
sequenceDiagram
    autonumber
    participant Client
    participant API as Presentation Layer
    participant Facade as Business Logic (Facade)
    participant DB as Persistence Layer

    Client->>API: POST /places (data + owner_id)
    API->>Facade: create_place(data)
    activate Facade
    Facade->>Facade: Validate Fields (Price, Lat/Lon, Amenities)
    
    alt Invalid Fields (e.g., Negative Price)
        Facade-->>API: Raise ValidationError
        API-->>Client: 400 Bad Request (Invalid input)
    else Fields Valid
        Facade->>DB: get_user(owner_id)
        alt Owner Not Found
            DB-->>Facade: None
            Facade-->>API: Raise NotFoundError
            API-->>Client: 404 Not Found (Owner missing)
        else Owner Exists
            DB-->>Facade: Return User_Object
            Facade->>Facade: Instantiate Place_Object
            Facade->>DB: save(Place_Object)
            activate DB
            DB-->>Facade: Confirm Save
            deactivate DB
            Facade-->>API: Return Place_Object
            API-->>Client: 201 Created (Place Data)
        end
    end
    deactivate Facade
```
### III. Review Submission
Flow Explanation: Reviews require multifaceted validation. The Facade verifies the rating constraints (e.g., 1-5 stars), ensures both the user_id and place_id exist, and crucially checks for duplicate reviews to prevent spam. All these constraints must be met before persisting the new record.

```mermaid
sequenceDiagram
    autonumber
    participant Client
    participant API as Presentation Layer
    participant Facade as Business Logic (Facade)
    participant DB as Persistence Layer

    Client->>API: POST /reviews (data + place_id + user_id)
    API->>Facade: create_review(data)
    activate Facade
    Facade->>Facade: validate_rating(data.rating)
    
    alt Invalid Rating
        Facade-->>API: Raise ValidationError
        API-->>Client: 400 Bad Request (Rating must be 1-5)
    else Rating Valid
        Facade->>DB: check_entities_exist(user_id, place_id)
        alt User or Place Not Found
            DB-->>Facade: Missing Entity
            Facade-->>API: Raise NotFoundError
            API-->>Client: 404 Not Found (Invalid User/Place)
        else Entities Valid
            DB-->>Facade: Entities Confirmed
            Facade->>DB: check_duplicate_review(user_id, place_id)
            alt Duplicate Review Exists
                DB-->>Facade: True
                Facade-->>API: Raise ConflictError
                API-->>Client: 409 Conflict (Review already exists)
            else No Duplicate
                DB-->>Facade: False
                Facade->>Facade: Instantiate Review_Object
                Facade->>DB: save(Review_Object)
                activate DB
                DB-->>Facade: Confirm Save
                deactivate DB
                Facade-->>API: Return Review_Object
                API-->>Client: 201 Created (Review Data)
            end
        end
    end
    deactivate Facade
```
### IV. Fetching a List of Places (With Filters)
Flow Explanation: A Read Operation based on specific search criteria (e.g., city, max_price). The API parses the query parameters and passes them to the Facade, which dynamically constructs a filtered lookup via the Persistence layer.

```mermaid
sequenceDiagram
    autonumber
    participant Client
    participant API as Presentation Layer
    participant Facade as Business Logic (Facade)
    participant DB as Persistence Layer

    Client->>API: GET /places?city=Riyadh&max_price=500
    API->>Facade: get_filtered_places(criteria)
    activate Facade
    Facade->>Facade: Parse and Validate Criteria
    
    alt Invalid Filter Parameters
        Facade-->>API: Raise ValidationError
        API-->>Client: 400 Bad Request (Invalid Filters)
    else Valid Criteria
        Facade->>DB: fetch_by_criteria(Place, criteria)
        activate DB
        DB-->>Facade: Return Filtered List~Place_Object~
        deactivate DB
        Facade-->>API: Return List~Place_Object~
        API->>API: Serialize Objects to JSON Array
        API-->>Client: 200 OK (Array of Filtered Places)
    end
    deactivate Facade

```
