#!/usr/bin/python3
"""Place API resources and serialization schemas."""
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from app.services import facade

api = Namespace('places', description='Place operations')

amenity_model = api.model('PlaceAmenity', {
    'id': fields.String(description='Amenity ID'),
    'name': fields.String(description='Name of the amenity'),
    'description': fields.String(description='Description of the amenity')
})

user_model = api.model('PlaceUser', {
    'id': fields.String(description='User ID'),
    'first_name': fields.String(description='First name of the owner'),
    'last_name': fields.String(description='Last name of the owner'),
    'email': fields.String(description='Email of the owner')
})

review_model = api.model('PlaceReview', {
    'id': fields.String(description='Review ID'),
    'text': fields.String(description='Review text'),
    'rating': fields.Integer(description='Rating, 1 to 5'),
    'user_id': fields.String(attribute=lambda review: review.user.id,
                               description='ID of the review author')
})

place_input_model = api.model('PlaceInput', {
    'title': fields.String(required=True, description='Title of the place'),
    'description': fields.String(description='Description of the place'),
    'price': fields.Float(required=True, description='Price per night'),
    'latitude': fields.Float(required=True, description='Latitude of the place'),
    'longitude': fields.Float(required=True, description='Longitude of the place'),
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
    'price': fields.Float(description='Price per night'),
    'latitude': fields.Float(description='Latitude of the place'),
    'longitude': fields.Float(description='Longitude of the place'),
    'owner': fields.Nested(user_model, description='Owner details'),
    'amenities': fields.List(fields.Nested(amenity_model),
                               description='List of amenities'),
    'reviews': fields.List(fields.Nested(review_model),
                           description='List of reviews')
})

place_update_model = api.model('PlaceUpdate', {
    'title': fields.String(description='Title of the place'),
    'description': fields.String(description='Description of the place'),
    'price': fields.Float(description='Price per night'),
    'amenities': fields.List(fields.String,
                               description="List of amenity IDs")
})

message_model = api.model('Message', {
    'message': fields.String(description='Status message')
})

@api.route('/')
class PlaceList(Resource):
    """Provide collection-level place operations."""

    @api.marshal_list_with(place_list_model)
    @api.response(200, 'List of places retrieved successfully')
    def get(self):
        """List all places."""
        return facade.get_all_places(), 200

    @api.expect(place_input_model, validate=True)
    @api.marshal_with(place_creation_response, code=201)
    @api.response(201, 'Place successfully created')
    @api.response(400, 'Invalid input data')
    @api.response(401, 'Missing or invalid token')
    @jwt_required()
    def post(self):
        """Register a new place with automatic owner assignment."""
        current_user_id = get_jwt_identity()
        data = api.payload
        
        # Set owner_id automatically from the authenticated user token
        data['owner_id'] = current_user_id

        try:
            place = facade.create_place(data)
            return place, 201
        except ValueError as e:
            api.abort(400, str(e))


@api.route('/<string:place_id>')
class PlaceResource(Resource):
    """Provide operations for an individual place."""

    @api.marshal_with(place_detail_model)
    @api.response(200, 'Place details retrieved successfully')
    @api.response(404, 'Place not found')
    def get(self, place_id):
        """Get place details, including its owner, amenities, and reviews."""
        place = facade.get_place(place_id)
        if not place:
            api.abort(404, 'Place not found')
        return place, 200

    @api.expect(place_update_model, validate=True)
    @api.response(200, 'Place updated successfully', message_model)
    @api.response(401, 'Missing or invalid token')
    @api.response(403, 'Unauthorized action')
    @api.response(404, 'Place not found')
    @api.response(400, 'Invalid input data')
    @jwt_required()
    def put(self, place_id):
        """Update a place's information with ownership verification."""
        current_user_id = get_jwt_identity()
        claims = get_jwt()
        is_admin = claims.get('is_admin', False)

        place = facade.get_place(place_id)
        if not place:
            api.abort(404, 'Place not found')

        owner_id = place.owner_id if hasattr(place, 'owner_id') else place.owner.id
        if owner_id != current_user_id and not is_admin:
            api.abort(403, 'Unauthorized action')

        try:
            facade.update_place(place_id, api.payload)
            return {"message": "Place updated successfully"}, 200
        except ValueError as e:
            api.abort(400, str(e))


@api.route('/<string:place_id>/reviews')
class PlaceReviewList(Resource):
    """Provide reviews associated with a place."""

    def get(self, place_id):
        """List reviews for a place."""
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
