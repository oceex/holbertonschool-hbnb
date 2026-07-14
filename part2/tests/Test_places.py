#!/usr/bin/python3
"""Unit tests for the Place API Endpoints."""

import json
import unittest
import uuid
from run import app


class TestPlaceEndpoints(unittest.TestCase):
    """Test cases for the Place API endpoints and logic rules."""

    def setUp(self):
        app.config['TESTING'] = True
        self.client = app.test_client()

        unique_email = f"owner_{uuid.uuid4()}@test.com"
        user_payload = {
            "first_name": "Test",
            "last_name": "Owner",
            "email": unique_email,
            "password": "password123"
        }
        res_user = self.client.post('/api/v1/users/', data=json.dumps(user_payload), content_type='application/json')
        self.owner_id = json.loads(res_user.data.decode('utf-8')).get('id')

    def test_create_place_success(self):
        payload = {
            "title": "Cozy Cabin",
            "price": 150.0,
            "latitude": 45.0,
            "longitude": -90.0,
            "owner_id": self.owner_id
        }
        response = self.client.post('/api/v1/places/', data=json.dumps(payload), content_type='application/json')
        
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(data['title'], 'Cozy Cabin')

    def test_create_place_invalid_latitude(self):
        payload = {
            "title": "Invalid Cabin",
            "price": 150.0,
            "latitude": 100.0,
            "longitude": -90.0,
            "owner_id": self.owner_id
        }
        response = self.client.post('/api/v1/places/', data=json.dumps(payload), content_type='application/json')
        self.assertEqual(response.status_code, 400)


if __name__ == '__main__':
    unittest.main()
