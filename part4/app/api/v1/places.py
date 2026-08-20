#!/usr/bin/python3
"""Place API resources and serialization schemas."""
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt

from app.services import facade


def current_user_is_admin():
    """Return whether the caller's JWT carries an is_admin=True claim."""
    return get_jwt().get("is_admin", False)


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

# The author's display name is nested here because GET /users/<id> requires a
# token; without it, reviews would be anonymous to signed-out visitors.
review_model = api.model('PlaceReview', {
    'id': fields.String(description='Review ID'),
    'text': fields.String(description='Review text'),
    'rating': fields.Integer(description='Rating, 1 to 5'),
    'user_id': fields.String(attribute=lambda review: review.user.id,
                             description='ID of the review author'),
    'author': fields.String(
        attribute=lambda review: '{} {}.'.format(
            review.user.first_name, review.user.last_name[:1]
        ),
        description='Display name of the review author'
    )
})

# 'owner_id' is deliberately absent: the owner comes from the caller's token,
# so nobody can create a place in someone else's name.
place_input_model = api.model('PlaceInput', {
    'title': fields.String(required=True, description='Title of the place'),
    'description': fields.String(description='Description of the place'),
    'price': fields.Float(required=True, description='Price per night'),
    'latitude': fields.Float(required=True, description='Latitude of the place'),
    'longitude': fields.Float(required=True, description='Longitude of the place'),
    'image_url': fields.String(description='Cover image URL for the place'),
    'location': fields.String(description='Short location label for the place'),
    'amenities': fields.List(fields.String, description="List of amenities ID's")
})

place_creation_response = api.model('PlaceCreationResponse', {
    'id': fields.String(description='Place ID'),
    'title': fields.String(description='Title of the place'),
    'description': fields.String(description='Description of the place'),
    'price': fields.Float(description='Price per night'),
    'latitude': fields.Float(description='Latitude of the place'),
    'longitude': fields.Float(description='Longitude of the place'),
    'image_url': fields.String(description='Cover image URL for the place'),
    'location': fields.String(description='Short location label for the place'),
    'owner_id': fields.String(attribute=lambda x: x.owner.id, description='ID of the owner')
})

place_list_model = api.model('PlaceList', {
    'id': fields.String(description='Place ID'),
    'title': fields.String(description='Title of the place'),
    'description': fields.String(description='Description of the place'),
    'price': fields.Float(description='Price per night'),
    'latitude': fields.Float(description='Latitude of the place'),
    'longitude': fields.Float(description='Longitude of the place'),
    'image_url': fields.String(description='Cover image URL for the place'),
    'location': fields.String(description='Short location label for the place')
})

place_detail_model = api.model('PlaceDetail', {
    'id': fields.String(description='Place ID'),
    'title': fields.String(description='Title of the place'),
    'description': fields.String(description='Description of the place'),
    'price': fields.Float(description='Price per night'),
    'latitude': fields.Float(description='Latitude of the place'),
    'longitude': fields.Float(description='Longitude of the place'),
    'image_url': fields.String(description='Cover image URL for the place'),
    'location': fields.String(description='Short location label for the place'),
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
    'image_url': fields.String(description='Cover image URL for the place'),
    'location': fields.String(description='Short location label for the place'),
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
        """List all places (Public)."""
        return facade.get_all_places(), 200

    @jwt_required()
    @api.expect(place_input_model, validate=True)
    @api.marshal_with(place_creation_response, code=201)
    @api.response(201, 'Place successfully created')
    @api.response(400, 'Invalid input data')
    @api.response(401, 'Missing or invalid token')
    def post(self):
        """Register a new place, owned by the authenticated user."""
        data = api.payload
        data['owner_id'] = get_jwt_identity()
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
        """Get place details (Public)."""
        place = facade.get_place(place_id)
        if not place:
            api.abort(404, 'Place not found')
        return place, 200

    @jwt_required()
    @api.expect(place_update_model, validate=True)
    @api.response(200, 'Place updated successfully', message_model)
    @api.response(403, 'Not the place owner')
    @api.response(404, 'Place not found')
    @api.response(400, 'Invalid input data')
    def put(self, place_id):
        """Update a place's information (owner or admin only)."""
        place = facade.get_place(place_id)
        if not place:
            api.abort(404, 'Place not found')

        if str(place.owner.id) != get_jwt_identity() and not current_user_is_admin():
            api.abort(403, 'Unauthorized action')

        try:
            facade.update_place(place_id, api.payload)
            return {"message": "Place updated successfully"}, 200
        except ValueError as e:
            api.abort(400, str(e))

    @jwt_required()
    @api.response(200, 'Place deleted successfully', message_model)
    @api.response(403, 'Not the place owner')
    @api.response(404, 'Place not found')
    def delete(self, place_id):
        """Delete a place (owner or admin only)."""
        place = facade.get_place(place_id)
        if not place:
            api.abort(404, 'Place not found')

        if str(place.owner.id) != get_jwt_identity() and not current_user_is_admin():
            api.abort(403, 'Unauthorized action')

        facade.delete_place(place_id)
        return {"message": "Place deleted successfully"}, 200


@api.route('/<string:place_id>/reviews')
class PlaceReviewList(Resource):
    """Provide reviews associated with a place."""

    def get(self, place_id):
        """List reviews for a place (Public)."""
        try:
            reviews = facade.get_reviews_by_place(place_id)
            return [{
                "id": r.id,
                "text": r.text,
                "rating": r.rating,
                "place_id": r.place.id,
                "user_id": r.user.id,
                "author": "{} {}.".format(
                    r.user.first_name, r.user.last_name[:1]
                )
            } for r in reviews], 200
        except ValueError as e:
            api.abort(404, str(e))
