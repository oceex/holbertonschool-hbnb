#!/usr/bin/python3
"""Unit tests for the User API Endpoints.

Verifies POST, GET, and PUT behavior for User management, including
validation rules for first_name, last_name, and email.
"""

import json
import unittest
import uuid
from run import app


class TestUserEndpoints(unittest.TestCase):
    """Test cases for the User API endpoints and validation rules."""

    def setUp(self):
        """Configure test client and set application config to testing mode."""
        app.config['TESTING'] = True
        self.client = app.test_client()

    def _unique_email(self):
        return f"user_{uuid.uuid4()}@test.com"

    # -- Successful creation ---------------------------------------------
    def test_create_user_success(self):
        """Verify successful creation of a user returns HTTP 201."""
        payload = {
            "first_name": "Jane",
            "last_name": "Doe",
            "email": self._unique_email(),
            "password": "password123",
        }
        response = self.client.post(
            '/api/v1/users/',
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data.decode('utf-8'))
        self.assertIn('id', data)
        self.assertEqual(data['first_name'], 'Jane')
        self.assertEqual(data['last_name'], 'Doe')
        self.assertFalse(data['is_admin'])

    # -- Required field validation ----------------------------------------
    def test_create_user_empty_first_name(self):
        """Verify empty first_name returns HTTP 400."""
        payload = {
            "first_name": "",
            "last_name": "Doe",
            "email": self._unique_email(),
            "password": "password123",
        }
        response = self.client.post(
            '/api/v1/users/',
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)

    def test_create_user_empty_last_name(self):
        """Verify empty last_name returns HTTP 400."""
        payload = {
            "first_name": "Jane",
            "last_name": "",
            "email": self._unique_email(),
            "password": "password123",
        }
        response = self.client.post(
            '/api/v1/users/',
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)

    def test_create_user_invalid_email_format(self):
        """Verify an invalid email format returns HTTP 400."""
        payload = {
            "first_name": "Jane",
            "last_name": "Doe",
            "email": "invalid-email",
            "password": "password123",
        }
        response = self.client.post(
            '/api/v1/users/',
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)

    def test_create_user_missing_email(self):
        """Verify a missing required email field returns HTTP 400."""
        payload = {
            "first_name": "Jane",
            "last_name": "Doe",
            "password": "password123",
        }
        response = self.client.post(
            '/api/v1/users/',
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)

    def test_create_user_duplicate_email(self):
        """Verify creating a user with an already-registered email returns HTTP 400."""
        email = self._unique_email()
        payload = {
            "first_name": "Jane",
            "last_name": "Doe",
            "email": email,
            "password": "password123",
        }
        first = self.client.post(
            '/api/v1/users/',
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(first.status_code, 201)

        second = self.client.post(
            '/api/v1/users/',
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(second.status_code, 400)

    # -- Retrieval ----------------------------------------------------------
    def test_get_all_users(self):
        """Verify retrieving all users returns HTTP 200 and a list."""
        response = self.client.get('/api/v1/users/')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode('utf-8'))
        self.assertIsInstance(data, list)

    def test_get_user_by_id_success(self):
        """Verify retrieving an existing user by id returns HTTP 200."""
        payload = {
            "first_name": "Jane",
            "last_name": "Doe",
            "email": self._unique_email(),
            "password": "password123",
        }
        create_response = self.client.post(
            '/api/v1/users/',
            data=json.dumps(payload),
            content_type='application/json'
        )
        user_id = json.loads(create_response.data.decode('utf-8'))['id']

        response = self.client.get(f'/api/v1/users/{user_id}')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(data['id'], user_id)

    def test_get_user_by_id_not_found(self):
        """Verify requesting a non-existent user ID returns HTTP 404."""
        response = self.client.get('/api/v1/users/non-existent-id')
        self.assertEqual(response.status_code, 404)

    # -- Update ---------------------------------------------------------------
    def test_update_user_success(self):
        """Verify updating a user's first_name returns HTTP 200."""
        payload = {
            "first_name": "Jane",
            "last_name": "Doe",
            "email": self._unique_email(),
            "password": "password123",
        }
        create_response = self.client.post(
            '/api/v1/users/',
            data=json.dumps(payload),
            content_type='application/json'
        )
        user_id = json.loads(create_response.data.decode('utf-8'))['id']

        update_payload = {"first_name": "Janet"}
        response = self.client.put(
            f'/api/v1/users/{user_id}',
            data=json.dumps(update_payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(data['first_name'], 'Janet')

    def test_update_user_not_found(self):
        """Verify updating a non-existent user returns HTTP 404."""
        update_payload = {"first_name": "Janet"}
        response = self.client.put(
            '/api/v1/users/non-existent-id',
            data=json.dumps(update_payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 404)

    def test_update_user_invalid_email(self):
        """Verify updating a user with an invalid email returns HTTP 400."""
        payload = {
            "first_name": "Jane",
            "last_name": "Doe",
            "email": self._unique_email(),
            "password": "password123",
        }
        create_response = self.client.post(
            '/api/v1/users/',
            data=json.dumps(payload),
            content_type='application/json'
        )
        user_id = json.loads(create_response.data.decode('utf-8'))['id']

        update_payload = {"email": "not-an-email"}
        response = self.client.put(
            f'/api/v1/users/{user_id}',
            data=json.dumps(update_payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)


if __name__ == '__main__':
    unittest.main()
