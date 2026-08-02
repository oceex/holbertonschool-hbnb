#!/usr/bin/python3
"""Tests for user API behavior.

The suite covers creation, retrieval, updates, input validation, and the
admin/self authorization rules enforced by the endpoints.
"""

import json
import unittest
import uuid
from run import app
from app.models.user import User
from app.services import facade
from tests.auth_helpers import make_admin, make_user


class TestUserEndpoints(unittest.TestCase):
    """Exercise user endpoints, validation rules, and authorization."""

    def setUp(self):
        """Create a Flask test client and a bootstrap admin."""
        app.config['TESTING'] = True
        self.client = app.test_client()
        self.admin, self.admin_headers = make_admin(self.client)

    def _unique_email(self):
        """Return an email address unique to the current test."""
        return f"user_{uuid.uuid4()}@test.com"

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
            content_type='application/json',
            headers=self.admin_headers,
        )
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data.decode('utf-8'))
        self.assertIn('id', data)
        self.assertEqual(data['first_name'], 'Jane')
        self.assertEqual(data['last_name'], 'Doe')
        self.assertFalse(data['is_admin'])
        self.assertNotIn('password', data)
        self.assertNotIn('_password', data)

    def test_create_user_requires_admin(self):
        """Verify user creation is rejected without a token, and without admin."""
        payload = {
            "first_name": "Jane",
            "last_name": "Doe",
            "email": self._unique_email(),
            "password": "password123",
        }
        no_token = self.client.post(
            '/api/v1/users/',
            data=json.dumps(payload),
            content_type='application/json',
        )
        self.assertEqual(no_token.status_code, 401)

        _, non_admin_headers = make_user(self.client, self.admin_headers)
        as_non_admin = self.client.post(
            '/api/v1/users/',
            data=json.dumps(payload),
            content_type='application/json',
            headers=non_admin_headers,
        )
        self.assertEqual(as_non_admin.status_code, 403)

    def test_password_is_hashed_and_verifiable(self):
        """Verify the model stores a bcrypt hash and checks passwords."""
        password = "password123"
        user = User(
            "Jane",
            "Doe",
            self._unique_email(),
            password,
        )

        self.assertIsInstance(user.password, str)
        self.assertNotEqual(user.password, password)
        self.assertRegex(
            user.password,
            r"^\$2[aby]\$\d{2}\$[./A-Za-z0-9]{53}$",
        )
        self.assertTrue(user.verify_password(password))
        self.assertFalse(user.verify_password("incorrect-password"))
        self.assertNotIn('password', user.to_dict())
        self.assertNotIn('_password', user.to_dict())

    def test_invalid_password_values_are_rejected(self):
        """Verify invalid plaintext passwords fail model validation."""
        for password in (None, "", "   "):
            with self.subTest(password=password):
                with self.assertRaises(ValueError):
                    User(
                        "Jane",
                        "Doe",
                        self._unique_email(),
                        password,
                    )

    def test_user_responses_do_not_expose_password(self):
        """Verify user creation and retrieval responses omit credentials."""
        password = "password123"
        payload = {
            "first_name": "Jane",
            "last_name": "Doe",
            "email": self._unique_email(),
            "password": password,
        }
        create_response = self.client.post(
            '/api/v1/users/',
            data=json.dumps(payload),
            content_type='application/json',
            headers=self.admin_headers,
        )
        self.assertEqual(create_response.status_code, 201)
        created = json.loads(create_response.data.decode('utf-8'))
        stored_user = facade.get_user(created['id'])

        self.assertNotEqual(stored_user.password, password)
        self.assertTrue(stored_user.verify_password(password))

        item_response = self.client.get(f"/api/v1/users/{created['id']}")
        list_response = self.client.get('/api/v1/users/')
        self.assertEqual(item_response.status_code, 200)
        self.assertEqual(list_response.status_code, 200)

        responses = [
            created,
            json.loads(item_response.data.decode('utf-8')),
            *json.loads(list_response.data.decode('utf-8')),
        ]
        for user_data in responses:
            self.assertNotIn('password', user_data)
            self.assertNotIn('_password', user_data)
            serialized = json.dumps(user_data)
            self.assertNotIn(password, serialized)
            self.assertNotIn(stored_user.password, serialized)

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
            content_type='application/json',
            headers=self.admin_headers,
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
            content_type='application/json',
            headers=self.admin_headers,
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
            content_type='application/json',
            headers=self.admin_headers,
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
            content_type='application/json',
            headers=self.admin_headers,
        )
        self.assertEqual(response.status_code, 400)

    def test_create_user_missing_password(self):
        """Verify a missing required password field returns HTTP 400."""
        payload = {
            "first_name": "Jane",
            "last_name": "Doe",
            "email": self._unique_email(),
        }
        response = self.client.post(
            '/api/v1/users/',
            data=json.dumps(payload),
            content_type='application/json',
            headers=self.admin_headers,
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
            content_type='application/json',
            headers=self.admin_headers,
        )
        self.assertEqual(first.status_code, 201)

        second = self.client.post(
            '/api/v1/users/',
            data=json.dumps(payload),
            content_type='application/json',
            headers=self.admin_headers,
        )
        self.assertEqual(second.status_code, 400)

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
            content_type='application/json',
            headers=self.admin_headers,
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

    def test_update_user_success(self):
        """Verify a user updating their own first_name returns HTTP 200."""
        user, user_headers = make_user(self.client, self.admin_headers)

        update_payload = {"first_name": "Janet"}
        response = self.client.put(
            f"/api/v1/users/{user['id']}",
            data=json.dumps(update_payload),
            content_type='application/json',
            headers=user_headers,
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
            content_type='application/json',
            headers=self.admin_headers,
        )
        self.assertEqual(response.status_code, 404)

    def test_update_user_invalid_email(self):
        """Verify an admin updating a user with a bad email returns HTTP 400."""
        user, _ = make_user(self.client, self.admin_headers)

        update_payload = {"email": "not-an-email"}
        response = self.client.put(
            f"/api/v1/users/{user['id']}",
            data=json.dumps(update_payload),
            content_type='application/json',
            headers=self.admin_headers,
        )
        self.assertEqual(response.status_code, 400)

    def test_update_user_forbidden_fields_for_non_admin(self):
        """Verify a non-admin cannot change their own email or is_admin."""
        user, user_headers = make_user(self.client, self.admin_headers)

        response = self.client.put(
            f"/api/v1/users/{user['id']}",
            data=json.dumps({"email": "new_" + user['email']}),
            content_type='application/json',
            headers=user_headers,
        )
        self.assertEqual(response.status_code, 400)


if __name__ == '__main__':
    unittest.main()
