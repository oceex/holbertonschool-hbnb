# Testing and Validation Report

## 1. Objective
Implement validation logic for all entity models (User, Place, Review, Amenity),
verify it through black-box cURL testing and Swagger documentation, and cover
it with an automated `unittest` suite — documenting successes and edge cases
along the way.

## 2. Validation Implementation

Validation lives in each model's property setters (`app/models/*.py`), so it's
enforced no matter how an object is constructed — not just through the API.

| Entity | Field | Rule |
| :--- | :--- | :--- |
| User | `first_name`, `last_name` | Required, non-empty string, max 50 chars |
| User | `email` | Required, must match a valid email pattern, must be unique |
| User | `password` | Required, non-empty string |
| User | `is_admin` | Must be a boolean |
| Place | `title` | Required, non-empty string, max 100 chars *(added in this task)* |
| Place | `price` | Must be numeric and >= 0 |
| Place | `latitude` | Must be numeric, between -90.0 and 90.0 inclusive |
| Place | `longitude` | Must be numeric, between -180.0 and 180.0 inclusive |
| Place | `owner_id` | Must reference an existing User (checked in the Facade) |
| Review | `text` | Required, non-empty string |
| Review | `rating` | Must be an integer between 1 and 5 inclusive |
| Review | `place_id` / `user_id` | Must reference existing Place/User entities |
| Review | (business rule) | A User may only review a given Place once |
| Amenity | `name` | Required, non-empty string, max 50 chars |

**Fix made in this task:** `Place.title` had no validation before this task —
an empty title was silently accepted. Added a setter that rejects empty/blank
titles and enforces a 100-character max, matching the pattern used elsewhere
in the codebase.

Invalid input raises `ValueError` from the model layer. The API layer
(`app/api/v1/*.py`) catches this in each `POST`/`PUT` handler and converts it
to an HTTP `400 Bad Request` via `api.abort(400, str(e))`. Flask-RESTx's
`@api.expect(model, validate=True)` also rejects requests that are missing
required fields or have the wrong JSON types, before the request even reaches
the Facade.

## 3. Black-Box Testing via cURL

Start the server first:
```bash
python3 run.py
```

### 3.1 User endpoints

**Create a valid user — expect 201**
```bash
curl -X POST "http://127.0.0.1:5000/api/v1/users/" \
  -H "Content-Type: application/json" \
  -d '{"first_name": "John", "last_name": "Doe", "email": "john.doe@example.com", "password": "secret123"}'
```
Expected: `201 Created`, JSON body with a generated `id`.

**Empty first_name — expect 400**
```bash
curl -X POST "http://127.0.0.1:5000/api/v1/users/" \
  -H "Content-Type: application/json" \
  -d '{"first_name": "", "last_name": "Doe", "email": "invalid-email", "password": "x"}'
```
Expected: `400 Bad Request`.

**Duplicate email — expect 400**
```bash
curl -X POST "http://127.0.0.1:5000/api/v1/users/" \
  -H "Content-Type: application/json" \
  -d '{"first_name": "Jane", "last_name": "Doe", "email": "john.doe@example.com", "password": "secret123"}'
```
Expected: `400 Bad Request`, `"Email already registered"`.

**Get non-existent user — expect 404**
```bash
curl "http://127.0.0.1:5000/api/v1/users/does-not-exist"
```
Expected: `404 Not Found`.

### 3.2 Place endpoints

**Create a valid place — expect 201**
```bash
curl -X POST "http://127.0.0.1:5000/api/v1/places/" \
  -H "Content-Type: application/json" \
  -d '{"title": "Cozy Cabin", "price": 150.0, "latitude": 45.0, "longitude": -90.0, "owner_id": "<owner-id>"}'
```
Expected: `201 Created`.

**Empty title — expect 400 (regression test for the fix in this task)**
```bash
curl -X POST "http://127.0.0.1:5000/api/v1/places/" \
  -H "Content-Type: application/json" \
  -d '{"title": "", "price": 150.0, "latitude": 45.0, "longitude": -90.0, "owner_id": "<owner-id>"}'
```
Expected: `400 Bad Request`. *(Previously returned 201 before the fix.)*

**Negative price — expect 400**
```bash
curl -X POST "http://127.0.0.1:5000/api/v1/places/" \
  -H "Content-Type: application/json" \
  -d '{"title": "Cheap Cabin", "price": -10, "latitude": 45.0, "longitude": -90.0, "owner_id": "<owner-id>"}'
```
Expected: `400 Bad Request`.

**Out-of-range latitude (boundary test) — expect 400**
```bash
curl -X POST "http://127.0.0.1:5000/api/v1/places/" \
  -H "Content-Type: application/json" \
  -d '{"title": "Invalid Cabin", "price": 150.0, "latitude": 100.0, "longitude": -90.0, "owner_id": "<owner-id>"}'
```
Expected: `400 Bad Request`.

**Exact boundary values (90 / -180) — expect 201**
```bash
curl -X POST "http://127.0.0.1:5000/api/v1/places/" \
  -H "Content-Type: application/json" \
  -d '{"title": "Edge of the World", "price": 99.0, "latitude": 90.0, "longitude": -180.0, "owner_id": "<owner-id>"}'
```
Expected: `201 Created` — boundary values are inclusive.

**Non-existent owner_id — expect 400**
```bash
curl -X POST "http://127.0.0.1:5000/api/v1/places/" \
  -H "Content-Type: application/json" \
  -d '{"title": "Orphan Cabin", "price": 150.0, "latitude": 45.0, "longitude": -90.0, "owner_id": "does-not-exist"}'
```
Expected: `400 Bad Request`.

### 3.3 Review endpoints

**Create a valid review — expect 201**
```bash
curl -X POST "http://127.0.0.1:5000/api/v1/reviews/" \
  -H "Content-Type: application/json" \
  -d '{"text": "Great stay!", "rating": 5, "place_id": "<place-id>", "user_id": "<user-id>"}'
```
Expected: `201 Created`.

**Rating out of range (boundary test) — expect 400**
```bash
curl -X POST "http://127.0.0.1:5000/api/v1/reviews/" \
  -H "Content-Type: application/json" \
  -d '{"text": "Too good", "rating": 6, "place_id": "<place-id>", "user_id": "<user-id>"}'
```
Expected: `400 Bad Request`.

**Non-existent place_id — expect 400**
```bash
curl -X POST "http://127.0.0.1:5000/api/v1/reviews/" \
  -H "Content-Type: application/json" \
  -d '{"text": "Nice", "rating": 4, "place_id": "does-not-exist", "user_id": "<user-id>"}'
```
Expected: `400 Bad Request`.

**Duplicate review by same user for same place — expect 400**
```bash
curl -X POST "http://127.0.0.1:5000/api/v1/reviews/" \
  -H "Content-Type: application/json" \
  -d '{"text": "Second attempt", "rating": 3, "place_id": "<place-id>", "user_id": "<user-id>"}'
```
Expected: `400 Bad Request` (a user may only review a given place once).

**Delete a non-existent review — expect 404**
```bash
curl -X DELETE "http://127.0.0.1:5000/api/v1/reviews/does-not-exist"
```
Expected: `404 Not Found`.

### 3.4 Amenity endpoints

**Create a valid amenity — expect 201**
```bash
curl -X POST "http://127.0.0.1:5000/api/v1/amenities/" \
  -H "Content-Type: application/json" \
  -d '{"name": "Swimming Pool"}'
```
Expected: `201 Created`.

**Empty name — expect 400**
```bash
curl -X POST "http://127.0.0.1:5000/api/v1/amenities/" \
  -H "Content-Type: application/json" \
  -d '{"name": ""}'
```
Expected: `400 Bad Request`.

## 4. Swagger Documentation

Flask-RESTx auto-generates interactive API docs from the models declared in
each namespace (`app/api/v1/*.py`). Once the server is running, they're
available at:

```
http://127.0.0.1:5000/api/v1/
```

Each namespace (`users`, `places`, `reviews`, `amenities`) lists its routes,
expected request bodies, and response codes, and can be used to fire test
requests directly from the browser — useful as a second, independent check
against the cURL results above.

## 5. Automated Test Suite

Located in `tests/`, using Python's `unittest` against Flask's test client
(no live server required):

| File | Covers |
| :--- | :--- |
| `tests/test_users.py` | Create (success/duplicate/invalid email/empty names), get all, get by id (found/404), update (success/404/invalid email) |
| `tests/test_places.py` | Create (success/empty title/negative price/bad lat/bad long/boundary values/invalid owner), get all, get by id (found/404), update (success/404) |
| `tests/test_reviews.py` | Create (success/empty text/rating boundaries/invalid place/invalid user/duplicate), get all, get by id (404), get by place, update (success/invalid rating), delete (success/404) |
| `tests/test_amenities.py` | Create (success/empty name), get all, get by id (404), update |

Run the whole suite with:
```bash
cd part2
pip install -r requirements.txt
python3 -m pytest tests/ -v
```
or with plain `unittest`:
```bash
python3 -m unittest discover -s tests -v
```

**Note:** one existing test file, `Test_places.py`, was renamed to
`test_places.py` — pytest/unittest's default discovery pattern
(`test_*.py`) is case-sensitive on Linux and was silently skipping it.

## 6. Summary Table

| Endpoint | Scenario | Expected Status |
| :--- | :--- | :--- |
| POST /users/ | Valid creation | 201 |
| POST /users/ | Empty first/last name | 400 |
| POST /users/ | Invalid email format | 400 |
| POST /users/ | Duplicate email | 400 |
| GET /users/{id} | Not found | 404 |
| POST /places/ | Valid creation | 201 |
| POST /places/ | Empty title | 400 |
| POST /places/ | Negative price | 400 |
| POST /places/ | Latitude/longitude out of range | 400 |
| POST /places/ | Boundary lat/long (±90/±180) | 201 |
| POST /places/ | Invalid owner_id | 400 |
| POST /reviews/ | Valid creation | 201 |
| POST /reviews/ | Empty text | 400 |
| POST /reviews/ | Rating out of range (boundary) | 400 |
| POST /reviews/ | Invalid place_id / user_id | 400 |
| POST /reviews/ | Duplicate review | 400 |
| DELETE /reviews/{id} | Not found | 404 |
| POST /amenities/ | Valid creation | 201 |
| POST /amenities/ | Empty name | 400 |

## 7. Issues Found and Fixed

1. **`Place.title` had no validation** — an empty or missing title could be
   saved silently. Fixed by adding a property setter that rejects empty/blank
   strings and enforces a max length, and added a regression test
   (`test_create_place_empty_title`).
2. **`Test_places.py` naming** — capitalized filename was invisible to
   default test discovery. Renamed to `test_places.py`.
3. **Missing test coverage** — no automated tests existed for the User or
   Review endpoints. Added `tests/test_users.py` and `tests/test_reviews.py`
   covering required-field validation, boundary conditions, foreign-key
   checks, and 404 handling.

## 8. Conclusion

All four entity models now enforce their documented validation rules at the
model layer, and those rules are exercised end-to-end through the API by an
automated test suite covering success paths, required-field violations,
boundary values, and not-found cases. Manual cURL testing and the Swagger UI
were used to independently confirm the same behavior.
