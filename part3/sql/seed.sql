PRAGMA foreign_keys = ON;
BEGIN TRANSACTION;

INSERT INTO users (
    id,
    first_name,
    last_name,
    email,
    password,
    is_admin
) VALUES (
    '36c9050e-ddd3-4c3b-9731-9f487208bbc1',
    'Admin',
    'HBnB',
    'admin@hbnb.io',
    '$2b$12$XEqrMOylxdCOp9orihk3NuySUys3LXH0u9s6NrsnI4a4rsEgV1Moi',
    TRUE
);

INSERT INTO amenities (id, name) VALUES
    ('df459d1d-1d1f-46cd-83ad-643723c3b84e', 'WiFi'),
    ('c1ee6cfe-26b0-4887-81c5-fbc04f0c6732', 'Swimming Pool'),
    ('cb7ec7b2-c15b-443b-bd68-386a0c9b55d7', 'Air Conditioning');

COMMIT;
