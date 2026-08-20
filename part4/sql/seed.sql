-- Initial data: the fixed administrator account and the starter amenities.
-- POST /api/v1/users/ is admin-only, so this account is what bootstraps the
-- very first login.

PRAGMA foreign_keys = ON;
BEGIN TRANSACTION;

INSERT INTO users (
    id,
    first_name,
    last_name,
    email,
    password,
    is_admin,
    created_at,
    updated_at
) VALUES (
    '36c9050e-ddd3-4c3b-9731-9f487208bbc1',
    'Admin',
    'HBnB',
    'admin@hbnb.io',
    -- bcrypt hash of 'admin1234'
    '$2b$12$XEqrMOylxdCOp9orihk3NuySUys3LXH0u9s6NrsnI4a4rsEgV1Moi',
    TRUE,
    CURRENT_TIMESTAMP,
    CURRENT_TIMESTAMP
);

INSERT INTO amenities (id, name, description, created_at, updated_at) VALUES
    ('df459d1d-1d1f-46cd-83ad-643723c3b84e', 'WiFi', '',
     CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('c1ee6cfe-26b0-4887-81c5-fbc04f0c6732', 'Swimming Pool', '',
     CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('cb7ec7b2-c15b-443b-bd68-386a0c9b55d7', 'Air Conditioning', '',
     CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);

COMMIT;
