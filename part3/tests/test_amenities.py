#!/usr/bin/python3
"""Tests for amenity API behavior.

The suite covers creation, retrieval, updates, and input validation.
"""

import json
import unittest
from run import app


class TestAmenityEndpoints(unittest.TestCase):
    """Exercise amenity endpoints and validation rules."""

    def setUp(self):
        """Create a Flask test client."""
        app.config['TESTING'] = True
        self.client = app.test_client()

    def test_create_amenity_success(self):
        """Verify successful creation of an amenity returns HTTP 201."""
        payload = {
            "name": "Swimming Pool",
            "description": "Outdoor heated pool",
        }
        response = self.client.post(
            '/api/v1/amenities/',
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data.decode('utf-8'))
        self.assertIn('id', data)
        self.assertEqual(data['name'], 'Swimming Pool')
        self.assertEqual(data['description'], 'Outdoor heated pool')

    def test_create_amenity_invalid_input(self):
        """Verify that creating an amenity with invalid payload returns HTTP 400."""
        payload = {"name": ""}
        response = self.client.post(
            '/api/v1/amenities/',
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)

    def test_create_amenity_missing_name(self):
        """Verify a missing required amenity name returns HTTP 400."""
        response = self.client.post(
            '/api/v1/amenities/',
            data=json.dumps({"description": "Missing name"}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)

    def test_get_all_amenities(self):
        """Verify amenity listings include descriptions."""
        create_response = self.client.post(
            '/api/v1/amenities/',
            data=json.dumps({
                "name": "Gym",
                "description": "Open 24 hours",
            }),
            content_type='application/json'
        )
        amenity_id = json.loads(
            create_response.data.decode('utf-8')
        )['id']

        response = self.client.get('/api/v1/amenities/')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode('utf-8'))
        self.assertIsInstance(data, list)
        amenity = next(item for item in data if item['id'] == amenity_id)
        self.assertEqual(amenity['description'], 'Open 24 hours')

    def test_get_amenity_by_id_not_found(self):
        """Verify that requesting a non-existent amenity ID returns HTTP 404."""
        response = self.client.get('/api/v1/amenities/non-existent-id')
        self.assertEqual(response.status_code, 404)

    def test_get_amenity_by_id_success(self):
        """Verify an amenity response includes its description."""
        create_response = self.client.post(
            '/api/v1/amenities/',
            data=json.dumps({
                "name": "Parking",
                "description": "Covered parking",
            }),
            content_type='application/json'
        )
        amenity_id = json.loads(
            create_response.data.decode('utf-8')
        )['id']

        response = self.client.get(f'/api/v1/amenities/{amenity_id}')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(data['description'], 'Covered parking')

    def test_update_amenity_success(self):
        """Verify an amenity description can be updated independently."""
        create_payload = {
            "name": "Pool",
            "description": "Outdoor pool",
        }
        create_response = self.client.post(
            '/api/v1/amenities/',
            data=json.dumps(create_payload),
            content_type='application/json'
        )
        amenity_id = json.loads(create_response.data.decode('utf-8'))['id']

        update_payload = {"description": "Indoor heated pool"}
        response = self.client.put(
            f'/api/v1/amenities/{amenity_id}',
            data=json.dumps(update_payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(data['message'], 'Amenity updated successfully')

        get_response = self.client.get(f'/api/v1/amenities/{amenity_id}')
        updated = json.loads(get_response.data.decode('utf-8'))
        self.assertEqual(updated['name'], 'Pool')
        self.assertEqual(updated['description'], 'Indoor heated pool')


if __name__ == '__main__':
    unittest.main()
