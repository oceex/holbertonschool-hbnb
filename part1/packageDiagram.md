```mermaid
classDiagram
    %% ==========================================
    %% EXPLANATORY NOTES
    %% ==========================================
    %% 1. Presentation Layer: 
    %% This layer handles the interaction between the user and the application. 
    %% It includes all the services and APIs that are exposed to the users.
    %% 
    %% 2. Business Logic Layer: 
    %% This layer contains the core business logic and the models that represent 
    %% the entities in the system (e.g., User, Place, Review, Amenity).
    %% 
    %% 3. Persistence Layer: 
    %% This layer is responsible for data storage and retrieval, 
    %% interacting directly with the database.
    %% 
    %% 4. The Facade Pattern: 
    %% A design pattern that provides a simple interface to a complex subsystem. 
    %% It helps hide the internal workings of the business logic and allows 
    %% the Presentation Layer (like APIs) to interact with internal services 
    %% more easily and cleanly.
    %% ==========================================

    class PresentationLayer {
        <<Package>>
        +API_Endpoints
        +Services
    }

    class BusinessLogicLayer {
        <<Package>>
        +HBnBFacade
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
    PresentationLayer ..> BusinessLogicLayer : Facade Pattern
    BusinessLogicLayer ..> PersistenceLayer : Database Operations
