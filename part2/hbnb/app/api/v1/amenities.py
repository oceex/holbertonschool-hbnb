#!/usr/bin/python3
"""Amenities API Namespace.

Provides RESTful endpoints for managing amenities including registration,
retrieval, and updates. This namespace handles JSON serialization and validation
rules for input payloads.
"""

from flask_restx import Namespace, Resource, fields
from app.services import facade

api = Namespace('amenities', description='Amenity operations')

amenity_model = api.model('Amenity', {
    'name': fields.String(required=True, description='Name of the amenity', max_length=50)
})

amenity_response_model = api.model('AmenityResponse', {
    'id': fields.String(readonly=True, description='Amenity unique ID'),
    'name': fields.String(description='Name of the amenity'),
    'created_at': fields.String(readonly=True, description='Creation timestamp'),
    'updated_at': fields.String(readonly=True, description='Last update timestamp')
})

message_model = api.model('Message', {
    'message': fields.String(description='Status message')
})


@api.route('/')
class AmenityList(Resource):
    """Resource managing creation and retrieval of lists of amenities."""

    @api.marshal_list_with(amenity_response_model)
    @api.response(200, 'List of amenities retrieved successfully')
    def get(self):
        """Retrieve a list of all amenities."""
        return facade.get_all_amenities(), 200

    @api.expect(amenity_model, validate=True)
    @api.marshal_with(amenity_response_model, code=201)
    @api.response(201, 'Amenity successfully created')
    @api.response(400, 'Invalid input data')
    def post(self):
        """Register a new amenity in the system."""
        try:
            amenity = facade.create_amenity(api.payload)
            return amenity, 201
        except ValueError as e:
            api.abort(400, str(e))


@api.route('/<string:amenity_id>')
class AmenityResource(Resource):
    """Resource managing operations on an individual amenity instance."""

    @api.marshal_with(amenity_response_model)
    @api.response(200, 'Amenity details retrieved successfully')
    @api.response(404, 'Amenity not found')
    def get(self, amenity_id):
        """Get details of a specific amenity by its ID."""
        amenity = facade.get_amenity(amenity_id)
        if not amenity:
            api.abort(404, 'Amenity not found')
        return amenity, 200

    @api.expect(amenity_model, validate=True)
    @api.response(200, 'Amenity updated successfully', message_model)
    @api.response(404, 'Amenity not found')
    @api.response(400, 'Invalid input data')
    def put(self, amenity_id):
        """Update an existing amenity's information by ID."""
        amenity = facade.get_amenity(amenity_id)
        if not amenity:
            api.abort(404, 'Amenity not found')

        try:
            facade.update_amenity(amenity_id, api.payload)
            return {"message": "Amenity updated successfully"}, 200
        except ValueError as e:
            api.abort(400, str(e))
