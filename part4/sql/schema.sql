-- Schema for the HBnB database. Column names and types mirror the mapped
-- models in app/models/, so a database built from this file and one built by
-- SQLAlchemy stay interchangeable.

PRAGMA foreign_keys = ON;
BEGIN TRANSACTION;

CREATE TABLE users (
    id CHAR(36),
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    email VARCHAR(120),
    password VARCHAR(128),
    is_admin BOOLEAN DEFAULT FALSE NOT NULL,
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL,
    CONSTRAINT pk_users PRIMARY KEY (id),
    CONSTRAINT uq_users_email UNIQUE (email)
);

CREATE TABLE amenities (
    id CHAR(36),
    name VARCHAR(50),
    description VARCHAR(1000) DEFAULT '' NOT NULL,
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL,
    CONSTRAINT pk_amenities PRIMARY KEY (id),
    CONSTRAINT uq_amenities_name UNIQUE (name)
);

CREATE TABLE places (
    id CHAR(36),
    title VARCHAR(100),
    description VARCHAR(1000) DEFAULT '' NOT NULL,
    price DECIMAL(10, 2),
    latitude FLOAT,
    longitude FLOAT,
    image_url VARCHAR(500),
    location VARCHAR(150),
    owner_id CHAR(36),
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL,
    CONSTRAINT pk_places PRIMARY KEY (id),
    CONSTRAINT fk_places_owner
        FOREIGN KEY (owner_id) REFERENCES users (id)
);

CREATE TABLE reviews (
    id CHAR(36),
    text VARCHAR(1000),
    rating INT,
    user_id CHAR(36),
    place_id CHAR(36),
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL,
    CONSTRAINT pk_reviews PRIMARY KEY (id),
    CONSTRAINT chk_reviews_rating CHECK (rating BETWEEN 1 AND 5),
    -- One review per user per place, matching the rule the facade enforces.
    CONSTRAINT uq_reviews_user_place UNIQUE (user_id, place_id),
    CONSTRAINT fk_reviews_user
        FOREIGN KEY (user_id) REFERENCES users (id),
    CONSTRAINT fk_reviews_place
        FOREIGN KEY (place_id) REFERENCES places (id)
);

CREATE TABLE place_amenity (
    place_id CHAR(36),
    amenity_id CHAR(36),
    CONSTRAINT pk_place_amenity PRIMARY KEY (place_id, amenity_id),
    CONSTRAINT fk_place_amenity_place
        FOREIGN KEY (place_id) REFERENCES places (id),
    CONSTRAINT fk_place_amenity_amenity
        FOREIGN KEY (amenity_id) REFERENCES amenities (id)
);

COMMIT;
