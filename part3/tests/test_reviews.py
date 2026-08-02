#!/usr/bin/python3
"""Tests for review API behavior.

The suite covers lifecycle operations, validation, and entity references.
"""

import json
import unittest
import uuid
from run import app
from app.services import facade
from tests.auth_helpers import make_admin, make_user


class TestReviewEndpoints(unittest.TestCase):
    """Exercise review endpoints and validation rules."""

    def setUp(self):
        """Create a test client with a place owner, a reviewer, and a place.

        The owner and the reviewer must be two different users: the API
        forbids a user from reviewing their own place, so self.user_id
        below refers to the *reviewer*, not the place owner.
        """
        app.config['TESTING'] = True
        self.client = app.test_client()

        self.admin, self.admin_headers = make_admin(self.client)

        owner, self.owner_headers = make_user(self.client, self.admin_headers)
        self.owner_id = owner['id']

        reviewer, self.reviewer_headers = make_user(self.client, self.admin_headers)
        self.user_id = reviewer['id']

        place_payload = {
            "title": "Test Place",
            "price": 100.0,
            "latitude": 10.0,
            "longitude": 10.0,
            "owner_id": self.owner_id,
        }
        place_res = self.client.post(
            '/api/v1/places/',
            data=json.dumps(place_payload),
            content_type='application/json',
            headers=self.owner_headers,
        )
        self.place_id = json.loads(place_res.data.decode('utf-8'))['id']

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
            content_type='application/json',
            headers=self.reviewer_headers,
        )
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data.decode('utf-8'))
        self.assertIn('id', data)
        self.assertEqual(data['text'], 'Great place to stay!')
        self.assertEqual(data['rating'], 5)

    def test_create_review_requires_auth(self):
        """Verify creating a review without a token returns HTTP 401."""
        payload = {
            "text": "Great place to stay!",
            "rating": 5,
            "place_id": self.place_id,
        }
        response = self.client.post(
            '/api/v1/reviews/',
            data=json.dumps(payload),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 401)

    def test_create_review_rejects_own_place(self):
        """Verify the place owner cannot review their own place."""
        payload = {
            "text": "My own place is great!",
            "rating": 5,
            "place_id": self.place_id,
        }
        response = self.client.post(
            '/api/v1/reviews/',
            data=json.dumps(payload),
            content_type='application/json',
            headers=self.owner_headers,
        )
        self.assertEqual(response.status_code, 400)

    def test_create_review_empty_text(self):
        """Verify an empty text field returns HTTP 400."""
        place = facade.get_place(self.place_id)
        user = facade.get_user(self.user_id)
        place_review_count = len(place.reviews)
        user_review_count = len(user.reviews)
        payload = {
            "text": "",
            "rating": 4,
            "place_id": self.place_id,
            "user_id": self.user_id,
        }
        response = self.client.post(
            '/api/v1/reviews/',
            data=json.dumps(payload),
            content_type='application/json',
            headers=self.reviewer_headers,
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(len(place.reviews), place_review_count)
        self.assertEqual(len(user.reviews), user_review_count)

    def test_create_review_missing_rating(self):
        """Verify a missing required rating returns HTTP 400."""
        payload = {
            "text": "Missing rating",
            "place_id": self.place_id,
            "user_id": self.user_id,
        }
        response = self.client.post(
            '/api/v1/reviews/',
            data=json.dumps(payload),
            content_type='application/json',
            headers=self.reviewer_headers,
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
            content_type='application/json',
            headers=self.reviewer_headers,
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
            content_type='application/json',
            headers=self.reviewer_headers,
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
            content_type='application/json',
            headers=self.reviewer_headers,
        )
        self.assertEqual(response.status_code, 400)

    def test_create_review_invalid_user_id(self):
        """Verify the facade rejects a review from a non-existent user.

        This can no longer be triggered through the API: POST /reviews/
        always takes the author from the caller's JWT identity, never from
        client input. The rule still exists as a facade-level guarantee,
        so it's tested there directly.
        """
        with app.app_context():
            with self.assertRaises(ValueError):
                facade.create_review({
                    "text": "Nice place",
                    "rating": 4,
                    "place_id": self.place_id,
                    "user_id": "non-existent-user-id",
                })

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
            content_type='application/json',
            headers=self.reviewer_headers,
        )
        self.assertEqual(first.status_code, 201)

        payload["text"] = "Second review attempt"
        second = self.client.post(
            '/api/v1/reviews/',
            data=json.dumps(payload),
            content_type='application/json',
            headers=self.reviewer_headers,
        )
        self.assertEqual(second.status_code, 400)

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

    def test_get_review_by_id_success(self):
        """Verify retrieving an existing review returns its relationships."""
        create_response = self.client.post(
            '/api/v1/reviews/',
            data=json.dumps({
                "text": "Comfortable stay",
                "rating": 4,
                "place_id": self.place_id,
                "user_id": self.user_id,
            }),
            content_type='application/json',
            headers=self.reviewer_headers,
        )
        review_id = json.loads(
            create_response.data.decode('utf-8')
        )['id']

        response = self.client.get(f'/api/v1/reviews/{review_id}')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(data['id'], review_id)
        self.assertEqual(data['place_id'], self.place_id)
        self.assertEqual(data['user_id'], self.user_id)

    def test_get_reviews_by_place(self):
        """Verify place review endpoints expose the linked review."""
        payload = {
            "text": "Loved it",
            "rating": 5,
            "place_id": self.place_id,
            "user_id": self.user_id,
        }
        create_response = self.client.post(
            '/api/v1/reviews/',
            data=json.dumps(payload),
            content_type='application/json',
            headers=self.reviewer_headers,
        )
        response = self.client.get(f'/api/v1/places/{self.place_id}/reviews')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode('utf-8'))
        self.assertIsInstance(data, list)
        review_id = json.loads(
            create_response.data.decode('utf-8')
        )['id']
        self.assertEqual([review['id'] for review in data], [review_id])

        place_response = self.client.get(f'/api/v1/places/{self.place_id}')
        place_data = json.loads(place_response.data.decode('utf-8'))
        self.assertEqual(place_data['reviews'], [{
            "id": review_id,
            "text": "Loved it",
            "rating": 5,
            "user_id": self.user_id,
        }])

    def test_update_review_success(self):
        """Verify the author updating a review's text/rating returns HTTP 200."""
        payload = {
            "text": "Initial review",
            "rating": 3,
            "place_id": self.place_id,
            "user_id": self.user_id,
        }
        create_response = self.client.post(
            '/api/v1/reviews/',
            data=json.dumps(payload),
            content_type='application/json',
            headers=self.reviewer_headers,
        )
        review_id = json.loads(create_response.data.decode('utf-8'))['id']

        update_payload = {"text": "Updated review", "rating": 5}
        response = self.client.put(
            f'/api/v1/reviews/{review_id}',
            data=json.dumps(update_payload),
            content_type='application/json',
            headers=self.reviewer_headers,
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(data['text'], 'Updated review')
        self.assertEqual(data['rating'], 5)

    def test_update_review_forbidden_for_non_author(self):
        """Verify a non-author, non-admin user cannot update someone else's review."""
        payload = {
            "text": "Initial review",
            "rating": 3,
            "place_id": self.place_id,
            "user_id": self.user_id,
        }
        create_response = self.client.post(
            '/api/v1/reviews/',
            data=json.dumps(payload),
            content_type='application/json',
            headers=self.reviewer_headers,
        )
        review_id = json.loads(create_response.data.decode('utf-8'))['id']

        _, other_headers = make_user(self.client, self.admin_headers)
        response = self.client.put(
            f'/api/v1/reviews/{review_id}',
            data=json.dumps({"text": "Hijacked review"}),
            content_type='application/json',
            headers=other_headers,
        )
        self.assertEqual(response.status_code, 403)

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
            content_type='application/json',
            headers=self.reviewer_headers,
        )
        review_id = json.loads(create_response.data.decode('utf-8'))['id']

        update_payload = {"rating": 10}
        response = self.client.put(
            f'/api/v1/reviews/{review_id}',
            data=json.dumps(update_payload),
            content_type='application/json',
            headers=self.reviewer_headers,
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
            content_type='application/json',
            headers=self.reviewer_headers,
        )
        review_id = json.loads(create_response.data.decode('utf-8'))['id']

        response = self.client.delete(
            f'/api/v1/reviews/{review_id}',
            headers=self.reviewer_headers,
        )
        self.assertEqual(response.status_code, 200)

        follow_up = self.client.get(f'/api/v1/reviews/{review_id}')
        self.assertEqual(follow_up.status_code, 404)

        place_response = self.client.get(
            f'/api/v1/places/{self.place_id}/reviews'
        )
        place_reviews = json.loads(place_response.data.decode('utf-8'))
        self.assertNotIn(
            review_id,
            [review['id'] for review in place_reviews],
        )

    def test_delete_review_not_found(self):
        """Verify deleting a non-existent review returns HTTP 404."""
        response = self.client.delete(
            '/api/v1/reviews/non-existent-id',
            headers=self.reviewer_headers,
        )
        self.assertEqual(response.status_code, 404)


if __name__ == '__main__':
    unittest.main()
