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

    def test_create_place_invalid_longitude(self):
        """Verify a longitude outside -180/180 returns HTTP 400 (boundary test)."""
        payload = {
            "title": "Invalid Cabin",
            "price": 150.0,
            "latitude": 45.0,
            "longitude": 200.0,
            "owner_id": self.owner_id
        }
        response = self.client.post('/api/v1/places/', data=json.dumps(payload), content_type='application/json')
        self.assertEqual(response.status_code, 400)

    def test_create_place_boundary_latitude_longitude(self):
        """Verify exact boundary values (-90/90, -180/180) are accepted."""
        payload = {
            "title": "Edge of the World Cabin",
            "price": 99.0,
            "latitude": 90.0,
            "longitude": -180.0,
            "owner_id": self.owner_id
        }
        response = self.client.post('/api/v1/places/', data=json.dumps(payload), content_type='application/json')
        self.assertEqual(response.status_code, 201)

    def test_create_place_empty_title(self):
        """Verify an empty title returns HTTP 400."""
        payload = {
            "title": "",
            "price": 150.0,
            "latitude": 45.0,
            "longitude": -90.0,
            "owner_id": self.owner_id
        }
        response = self.client.post('/api/v1/places/', data=json.dumps(payload), content_type='application/json')
        self.assertEqual(response.status_code, 400)

    def test_create_place_negative_price(self):
        """Verify a negative price returns HTTP 400."""
        payload = {
            "title": "Cheap Cabin",
            "price": -10.0,
            "latitude": 45.0,
            "longitude": -90.0,
            "owner_id": self.owner_id
        }
        response = self.client.post('/api/v1/places/', data=json.dumps(payload), content_type='application/json')
        self.assertEqual(response.status_code, 400)

    def test_create_place_invalid_owner(self):
        """Verify a non-existent owner_id returns HTTP 400."""
        payload = {
            "title": "Orphan Cabin",
            "price": 150.0,
            "latitude": 45.0,
            "longitude": -90.0,
            "owner_id": "non-existent-owner-id"
        }
        response = self.client.post('/api/v1/places/', data=json.dumps(payload), content_type='application/json')
        self.assertEqual(response.status_code, 400)

    def test_get_all_places(self):
        """Verify retrieving all places returns HTTP 200 and a list."""
        response = self.client.get('/api/v1/places/')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode('utf-8'))
        self.assertIsInstance(data, list)

    def test_get_place_by_id_success(self):
        """Verify retrieving an existing place returns HTTP 200 with owner details."""
        payload = {
            "title": "Cozy Cabin",
            "price": 150.0,
            "latitude": 45.0,
            "longitude": -90.0,
            "owner_id": self.owner_id
        }
        create_response = self.client.post('/api/v1/places/', data=json.dumps(payload), content_type='application/json')
        place_id = json.loads(create_response.data.decode('utf-8'))['id']

        response = self.client.get(f'/api/v1/places/{place_id}')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(data['id'], place_id)
        self.assertIn('owner', data)

    def test_get_place_by_id_not_found(self):
        """Verify requesting a non-existent place ID returns HTTP 404."""
        response = self.client.get('/api/v1/places/non-existent-id')
        self.assertEqual(response.status_code, 404)

    def test_update_place_success(self):
        """Verify updating a place's title returns HTTP 200."""
        payload = {
            "title": "Cozy Cabin",
            "price": 150.0,
            "latitude": 45.0,
            "longitude": -90.0,
            "owner_id": self.owner_id
        }
        create_response = self.client.post('/api/v1/places/', data=json.dumps(payload), content_type='application/json')
        place_id = json.loads(create_response.data.decode('utf-8'))['id']

        update_payload = {"title": "Renovated Cabin"}
        response = self.client.put(
            f'/api/v1/places/{place_id}',
            data=json.dumps(update_payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)

    def test_update_place_not_found(self):
        """Verify updating a non-existent place returns HTTP 404."""
        update_payload = {"title": "Ghost Cabin"}
        response = self.client.put(
            '/api/v1/places/non-existent-id',
            data=json.dumps(update_payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 404)


if __name__ == '__main__':
    unittest.main()
