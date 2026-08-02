#!/usr/bin/python3
"""Amenity API resources and serialization schemas."""
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt

from app.services import facade


def current_user_is_admin():
    """Return whether the caller's JWT carries an is_admin=True claim."""
    return get_jwt().get("is_admin", False)


api = Namespace('amenities', description='Amenity operations')

amenity_model = api.model('Amenity', {
    'name': fields.String(required=True, description='Name of the amenity',
                          max_length=50),
    'description': fields.String(description='Description of the amenity')
})

amenity_update_model = api.model('AmenityUpdate', {
    'name': fields.String(description='Name of the amenity', max_length=50),
    'description': fields.String(description='Description of the amenity')
})

amenity_response_model = api.model('AmenityResponse', {
    'id': fields.String(readonly=True, description='Amenity unique ID'),
    'name': fields.String(description='Name of the amenity'),
    'description': fields.String(description='Description of the amenity'),
    'created_at': fields.String(readonly=True, description='Creation timestamp'),
    'updated_at': fields.String(readonly=True, description='Last update timestamp')
})

message_model = api.model('Message', {
    'message': fields.String(description='Status message')
})


@api.route('/')
class AmenityList(Resource):
    """Provide collection-level amenity operations."""

    @api.marshal_list_with(amenity_response_model)
    @api.response(200, 'List of amenities retrieved successfully')
    def get(self):
        """List all amenities (Public)."""
        return facade.get_all_amenities(), 200

    @jwt_required()
    @api.expect(amenity_model, validate=True)
    @api.marshal_with(amenity_response_model, code=201)
    @api.response(201, 'Amenity successfully created')
    @api.response(400, 'Invalid input data')
    @api.response(403, 'Admin privileges required')
    def post(self):
        """Create an amenity (admin only)."""
        if not current_user_is_admin():
            api.abort(403, 'Admin privileges required')
        try:
            amenity = facade.create_amenity(api.payload)
            return amenity, 201
        except ValueError as e:
            api.abort(400, str(e))


@api.route('/<string:amenity_id>')
class AmenityResource(Resource):
    """Provide operations for an individual amenity."""

    @api.marshal_with(amenity_response_model)
    @api.response(200, 'Amenity details retrieved successfully')
    @api.response(404, 'Amenity not found')
    def get(self, amenity_id):
        """Get an amenity by ID (Public)."""
        amenity = facade.get_amenity(amenity_id)
        if not amenity:
            api.abort(404, 'Amenity not found')
        return amenity, 200

    @jwt_required()
    @api.expect(amenity_update_model, validate=True)
    @api.response(200, 'Amenity updated successfully', message_model)
    @api.response(404, 'Amenity not found')
    @api.response(400, 'Invalid input data')
    @api.response(403, 'Admin privileges required')
    def put(self, amenity_id):
        """Update an amenity (admin only)."""
        if not current_user_is_admin():
            api.abort(403, 'Admin privileges required')

        amenity = facade.get_amenity(amenity_id)
        if not amenity:
            api.abort(404, 'Amenity not found')

        try:
            facade.update_amenity(amenity_id, api.payload)
            return {"message": "Amenity updated successfully"}, 200
        except ValueError as e:
            api.abort(400, str(e))
