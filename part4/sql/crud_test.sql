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
    '11111111-1111-4111-8111-111111111111',
    'SQL',
    'Tester',
    'sql.tester@hbnb.local',
    '$2b$12$AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA',
    FALSE
);
SELECT id, first_name, last_name, email, is_admin
FROM users
WHERE id = '11111111-1111-4111-8111-111111111111';
UPDATE users
SET first_name = 'Updated SQL'
WHERE id = '11111111-1111-4111-8111-111111111111';

INSERT INTO amenities (id, name) VALUES (
    '22222222-2222-4222-8222-222222222222',
    'SQL Test Amenity'
);
SELECT id, name
FROM amenities
WHERE id = '22222222-2222-4222-8222-222222222222';
UPDATE amenities
SET name = 'Updated SQL Test Amenity'
WHERE id = '22222222-2222-4222-8222-222222222222';

INSERT INTO places (
    id,
    title,
    description,
    price,
    latitude,
    longitude,
    owner_id
) VALUES (
    '33333333-3333-4333-8333-333333333333',
    'SQL Test Place',
    'Created by the direct SQL CRUD demonstration.',
    100.00,
    24.7136,
    46.6753,
    '11111111-1111-4111-8111-111111111111'
);
SELECT id, title, price, owner_id
FROM places
WHERE id = '33333333-3333-4333-8333-333333333333';
UPDATE places
SET price = 125.00
WHERE id = '33333333-3333-4333-8333-333333333333';

INSERT INTO reviews (
    id,
    text,
    rating,
    user_id,
    place_id
) VALUES (
    '44444444-4444-4444-8444-444444444444',
    'Direct SQL review',
    4,
    '11111111-1111-4111-8111-111111111111',
    '33333333-3333-4333-8333-333333333333'
);
SELECT id, text, rating, user_id, place_id
FROM reviews
WHERE id = '44444444-4444-4444-8444-444444444444';
UPDATE reviews
SET rating = 5
WHERE id = '44444444-4444-4444-8444-444444444444';

INSERT INTO place_amenity (place_id, amenity_id) VALUES (
    '33333333-3333-4333-8333-333333333333',
    '22222222-2222-4222-8222-222222222222'
);
SELECT place_id, amenity_id
FROM place_amenity
WHERE place_id = '33333333-3333-4333-8333-333333333333'
  AND amenity_id = '22222222-2222-4222-8222-222222222222';

DELETE FROM place_amenity
WHERE place_id = '33333333-3333-4333-8333-333333333333'
  AND amenity_id = '22222222-2222-4222-8222-222222222222';
DELETE FROM reviews
WHERE id = '44444444-4444-4444-8444-444444444444';
DELETE FROM places
WHERE id = '33333333-3333-4333-8333-333333333333';
DELETE FROM amenities
WHERE id = '22222222-2222-4222-8222-222222222222';
DELETE FROM users
WHERE id = '11111111-1111-4111-8111-111111111111';

ROLLBACK;
