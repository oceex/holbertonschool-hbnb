#!/usr/bin/python3
"""Unit tests for the Amenity API Endpoints.

Verifies the correct operation of POST, GET, and PUT endpoints for Amenity management
using Flask's build-in test client.
"""

import json
import unittest
from run import app


class TestAmenityEndpoints(unittest.TestCase):
    """Test cases for the Amenity API endpoints."""

    def setUp(self):
        """Configure test client and set application config to testing mode."""
        app.config['TESTING'] = True
        self.client = app.test_client()

    def test_create_amenity_success(self):
        """Verify successful creation of an amenity returns HTTP 201."""
        payload = {"name": "Swimming Pool"}
        response = self.client.post(
            '/api/v1/amenities/',
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data.decode('utf-8'))
        self.assertIn('id', data)
        self.assertEqual(data['name'], 'Swimming Pool')

    def test_create_amenity_invalid_input(self):
        """Verify that creating an amenity with invalid payload returns HTTP 400."""
        payload = {"name": ""}
        response = self.client.post(
            '/api/v1/amenities/',
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)

    def test_get_all_amenities(self):
        """Verify retrieving all amenities returns HTTP 200 and a list."""
        response = self.client.get('/api/v1/amenities/')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode('utf-8'))
        self.assertIsInstance(data, list)

    def test_get_amenity_by_id_not_found(self):
        """Verify that requesting a non-existent amenity ID returns HTTP 404."""
        response = self.client.get('/api/v1/amenities/non-existent-id')
        self.assertEqual(response.status_code, 404)

    def test_update_amenity_success(self):
        """Verify that updating an amenity returns HTTP 200 and success message."""
        create_payload = {"name": "Old Pool"}
        create_response = self.client.post(
            '/api/v1/amenities/',
            data=json.dumps(create_payload),
            content_type='application/json'
        )
        amenity_id = json.loads(create_response.data.decode('utf-8'))['id']

        update_payload = {"name": "Luxury Pool"}
        response = self.client.put(
            f'/api/v1/amenities/{amenity_id}',
            data=json.dumps(update_payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(data['message'], 'Amenity updated successfully')


if __name__ == '__main__':
    unittest.main()
