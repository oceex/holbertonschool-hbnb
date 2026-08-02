PRAGMA foreign_keys = ON;
BEGIN TRANSACTION;

CREATE TABLE users (
    id CHAR(36),
    first_name VARCHAR(255),
    last_name VARCHAR(255),
    email VARCHAR(255),
    password VARCHAR(255),
    is_admin BOOLEAN DEFAULT FALSE,
    CONSTRAINT pk_users PRIMARY KEY (id),
    CONSTRAINT uq_users_email UNIQUE (email)
);

CREATE TABLE amenities (
    id CHAR(36),
    name VARCHAR(255),
    CONSTRAINT pk_amenities PRIMARY KEY (id),
    CONSTRAINT uq_amenities_name UNIQUE (name)
);

CREATE TABLE places (
    id CHAR(36),
    title VARCHAR(255),
    description TEXT,
    price DECIMAL(10, 2),
    latitude FLOAT,
    longitude FLOAT,
    owner_id CHAR(36),
    CONSTRAINT pk_places PRIMARY KEY (id),
    CONSTRAINT fk_places_owner
        FOREIGN KEY (owner_id) REFERENCES users (id)
);

CREATE TABLE reviews (
    id CHAR(36),
    text TEXT,
    rating INT,
    user_id CHAR(36),
    place_id CHAR(36),
    CONSTRAINT pk_reviews PRIMARY KEY (id),
    CONSTRAINT chk_reviews_rating CHECK (rating BETWEEN 1 AND 5),
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
