#!/usr/bin/python3
"""Unit tests for the Review API Endpoints.

Verifies POST, GET, PUT, and DELETE behavior for Review management,
including validation of text, rating bounds, and foreign-key references
to Place and User.
"""

import json
import unittest
import uuid
from run import app


class TestReviewEndpoints(unittest.TestCase):
    """Test cases for the Review API endpoints and validation rules."""

    def setUp(self):
        """Configure the test client and create a User + Place fixture."""
        app.config['TESTING'] = True
        self.client = app.test_client()

        user_payload = {
            "first_name": "Test",
            "last_name": "Reviewer",
            "email": f"reviewer_{uuid.uuid4()}@test.com",
            "password": "password123",
        }
        user_res = self.client.post(
            '/api/v1/users/',
            data=json.dumps(user_payload),
            content_type='application/json'
        )
        self.user_id = json.loads(user_res.data.decode('utf-8'))['id']

        place_payload = {
            "title": "Test Place",
            "price": 100.0,
            "latitude": 10.0,
            "longitude": 10.0,
            "owner_id": self.user_id,
        }
        place_res = self.client.post(
            '/api/v1/places/',
            data=json.dumps(place_payload),
            content_type='application/json'
        )
        self.place_id = json.loads(place_res.data.decode('utf-8'))['id']

    # -- Successful creation ---------------------------------------------
    def test_create_review_success(self):
        """Verify successful creation of a review returns HTTP 201."""
        payload = {
            "text": "Great place to stay!",
            "rating": 5,
            "place_id": self.place_id,
            "user_id": self.user_id,
        }
        response = self.client.post(
            '/api/v1/reviews/',
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data.decode('utf-8'))
        self.assertIn('id', data)
        self.assertEqual(data['text'], 'Great place to stay!')
        self.assertEqual(data['rating'], 5)

    # -- Validation rules --------------------------------------------------
    def test_create_review_empty_text(self):
        """Verify an empty text field returns HTTP 400."""
        payload = {
            "text": "",
            "rating": 4,
            "place_id": self.place_id,
            "user_id": self.user_id,
        }
        response = self.client.post(
            '/api/v1/reviews/',
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)

    def test_create_review_rating_out_of_range_high(self):
        """Verify a rating above 5 returns HTTP 400 (boundary test)."""
        payload = {
            "text": "Too good to be true",
            "rating": 6,
            "place_id": self.place_id,
            "user_id": self.user_id,
        }
        response = self.client.post(
            '/api/v1/reviews/',
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)

    def test_create_review_rating_out_of_range_low(self):
        """Verify a rating below 1 returns HTTP 400 (boundary test)."""
        payload = {
            "text": "Terrible",
            "rating": 0,
            "place_id": self.place_id,
            "user_id": self.user_id,
        }
        response = self.client.post(
            '/api/v1/reviews/',
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)

    def test_create_review_invalid_place_id(self):
        """Verify a non-existent place_id returns HTTP 400."""
        payload = {
            "text": "Nice place",
            "rating": 4,
            "place_id": "non-existent-place-id",
            "user_id": self.user_id,
        }
        response = self.client.post(
            '/api/v1/reviews/',
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)

    def test_create_review_invalid_user_id(self):
        """Verify a non-existent user_id returns HTTP 400."""
        payload = {
            "text": "Nice place",
            "rating": 4,
            "place_id": self.place_id,
            "user_id": "non-existent-user-id",
        }
        response = self.client.post(
            '/api/v1/reviews/',
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)

    def test_create_duplicate_review_rejected(self):
        """Verify a user cannot review the same place twice."""
        payload = {
            "text": "First review",
            "rating": 4,
            "place_id": self.place_id,
            "user_id": self.user_id,
        }
        first = self.client.post(
            '/api/v1/reviews/',
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(first.status_code, 201)

        payload["text"] = "Second review attempt"
        second = self.client.post(
            '/api/v1/reviews/',
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(second.status_code, 400)

    # -- Retrieval ----------------------------------------------------------
    def test_get_all_reviews(self):
        """Verify retrieving all reviews returns HTTP 200 and a list."""
        response = self.client.get('/api/v1/reviews/')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode('utf-8'))
        self.assertIsInstance(data, list)

    def test_get_review_by_id_not_found(self):
        """Verify requesting a non-existent review ID returns HTTP 404."""
        response = self.client.get('/api/v1/reviews/non-existent-id')
        self.assertEqual(response.status_code, 404)

    def test_get_reviews_by_place(self):
        """Verify retrieving reviews for a specific place returns HTTP 200."""
        payload = {
            "text": "Loved it",
            "rating": 5,
            "place_id": self.place_id,
            "user_id": self.user_id,
        }
        self.client.post(
            '/api/v1/reviews/',
            data=json.dumps(payload),
            content_type='application/json'
        )
        response = self.client.get(f'/api/v1/places/{self.place_id}/reviews')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode('utf-8'))
        self.assertIsInstance(data, list)
        self.assertGreaterEqual(len(data), 1)

    # -- Update / Delete ------------------------------------------------------
    def test_update_review_success(self):
        """Verify updating a review's text/rating returns HTTP 200."""
        payload = {
            "text": "Initial review",
            "rating": 3,
            "place_id": self.place_id,
            "user_id": self.user_id,
        }
        create_response = self.client.post(
            '/api/v1/reviews/',
            data=json.dumps(payload),
            content_type='application/json'
        )
        review_id = json.loads(create_response.data.decode('utf-8'))['id']

        update_payload = {"text": "Updated review", "rating": 5}
        response = self.client.put(
            f'/api/v1/reviews/{review_id}',
            data=json.dumps(update_payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(data['text'], 'Updated review')
        self.assertEqual(data['rating'], 5)

    def test_update_review_invalid_rating(self):
        """Verify updating a review with an out-of-range rating returns HTTP 400."""
        payload = {
            "text": "Initial review",
            "rating": 3,
            "place_id": self.place_id,
            "user_id": self.user_id,
        }
        create_response = self.client.post(
            '/api/v1/reviews/',
            data=json.dumps(payload),
            content_type='application/json'
        )
        review_id = json.loads(create_response.data.decode('utf-8'))['id']

        update_payload = {"rating": 10}
        response = self.client.put(
            f'/api/v1/reviews/{review_id}',
            data=json.dumps(update_payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)

    def test_delete_review_success(self):
        """Verify deleting an existing review returns HTTP 200."""
        payload = {
            "text": "To be deleted",
            "rating": 2,
            "place_id": self.place_id,
            "user_id": self.user_id,
        }
        create_response = self.client.post(
            '/api/v1/reviews/',
            data=json.dumps(payload),
            content_type='application/json'
        )
        review_id = json.loads(create_response.data.decode('utf-8'))['id']

        response = self.client.delete(f'/api/v1/reviews/{review_id}')
        self.assertEqual(response.status_code, 200)

        # Confirm the review no longer exists
        follow_up = self.client.get(f'/api/v1/reviews/{review_id}')
        self.assertEqual(follow_up.status_code, 404)

    def test_delete_review_not_found(self):
        """Verify deleting a non-existent review returns HTTP 404."""
        response = self.client.delete('/api/v1/reviews/non-existent-id')
        self.assertEqual(response.status_code, 404)


if __name__ == '__main__':
    unittest.main()
