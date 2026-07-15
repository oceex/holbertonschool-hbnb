#!/usr/bin/python3
"""Places API Namespace.

Provides RESTful endpoints for Place entities, integrating nested
serialization for related Users and Amenities.
"""

from flask_restx import Namespace, Resource, fields
from app.services import facade

api = Namespace('places', description='Place operations')

# -- Nested Models -------------------------------------------------------------
amenity_model = api.model('PlaceAmenity', {
    'id': fields.String(description='Amenity ID'),
    'name': fields.String(description='Name of the amenity')
})

user_model = api.model('PlaceUser', {
    'id': fields.String(description='User ID'),
    'first_name': fields.String(description='First name of the owner'),
    'last_name': fields.String(description='Last name of the owner'),
    'email': fields.String(description='Email of the owner')
})

# -- Request/Response Models ---------------------------------------------------
place_input_model = api.model('PlaceInput', {
    'title': fields.String(required=True, description='Title of the place'),
    'description': fields.String(description='Description of the place'),
    'price': fields.Float(required=True, description='Price per night'),
    'latitude': fields.Float(required=True, description='Latitude of the place'),
    'longitude': fields.Float(required=True, description='Longitude of the place'),
    'owner_id': fields.String(required=True, description='ID of the owner'),
    'amenities': fields.List(fields.String, description="List of amenities ID's")
})

place_creation_response = api.model('PlaceCreationResponse', {
    'id': fields.String(description='Place ID'),
    'title': fields.String(description='Title of the place'),
    'description': fields.String(description='Description of the place'),
    'price': fields.Float(description='Price per night'),
    'latitude': fields.Float(description='Latitude of the place'),
    'longitude': fields.Float(description='Longitude of the place'),
    'owner_id': fields.String(attribute=lambda x: x.owner.id, description='ID of the owner')
})

place_list_model = api.model('PlaceList', {
    'id': fields.String(description='Place ID'),
    'title': fields.String(description='Title of the place'),
    'latitude': fields.Float(description='Latitude of the place'),
    'longitude': fields.Float(description='Longitude of the place')
})

place_detail_model = api.model('PlaceDetail', {
    'id': fields.String(description='Place ID'),
    'title': fields.String(description='Title of the place'),
    'description': fields.String(description='Description of the place'),
    'latitude': fields.Float(description='Latitude of the place'),
    'longitude': fields.Float(description='Longitude of the place'),
    'owner': fields.Nested(user_model, description='Owner details'),
    'amenities': fields.List(fields.Nested(amenity_model), description='List of amenities')
})

place_update_model = api.model('PlaceUpdate', {
    'title': fields.String(description='Title of the place'),
    'description': fields.String(description='Description of the place'),
    'price': fields.Float(description='Price per night')
})

message_model = api.model('Message', {
    'message': fields.String(description='Status message')
})


# -- API Routes ----------------------------------------------------------------

@api.route('/')
class PlaceList(Resource):
    """Resource managing creation and retrieval of place lists."""

    @api.marshal_list_with(place_list_model)
    @api.response(200, 'List of places retrieved successfully')
    def get(self):
        """Retrieve a list of all places."""
        return facade.get_all_places(), 200

    @api.expect(place_input_model, validate=True)
    @api.marshal_with(place_creation_response, code=201)
    @api.response(201, 'Place successfully created')
    @api.response(400, 'Invalid input data')
    def post(self):
        """Register a new place."""
        try:
            place = facade.create_place(api.payload)
            return place, 201
        except ValueError as e:
            api.abort(400, str(e))


@api.route('/<string:place_id>')
class PlaceResource(Resource):
    """Resource managing operations on an individual place instance."""

    @api.marshal_with(place_detail_model)
    @api.response(200, 'Place details retrieved successfully')
    @api.response(404, 'Place not found')
    def get(self, place_id):
        """Get place details by ID (Includes owner and amenities)."""
        place = facade.get_place(place_id)
        if not place:
            api.abort(404, 'Place not found')
        return place, 200

    @api.expect(place_update_model, validate=True)
    @api.response(200, 'Place updated successfully', message_model)
    @api.response(404, 'Place not found')
    @api.response(400, 'Invalid input data')
    def put(self, place_id):
        """Update a place's information."""
        place = facade.get_place(place_id)
        if not place:
            api.abort(404, 'Place not found')

        try:
            facade.update_place(place_id, api.payload)
            return {"message": "Place updated successfully"}, 200
        except ValueError as e:
            api.abort(400, str(e))

@api.route('/<string:place_id>/reviews')
class PlaceReviewList(Resource):
    """Resource for retrieving reviews associated with a specific place."""

    def get(self, place_id):
        """Get all reviews for a specific place."""
        try:
            reviews = facade.get_reviews_by_place(place_id)
            return [{
                "id": r.id,
                "text": r.text,
                "rating": r.rating,
                "place_id": r.place.id,
                "user_id": r.user.id
            } for r in reviews], 200
        except ValueError as e:
            api.abort(404, str(e))
