#!/usr/bin/python3
"""Review API resources and serialization schemas."""
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services import facade

api = Namespace("reviews", description="Review operations")

review_model = api.model("Review", {
    "text": fields.String(required=True, description="Review text"),
    "rating": fields.Integer(required=True, description="Rating, 1 to 5"),
    "place_id": fields.String(required=True, description="Place id"),
})

review_update_model = api.model("ReviewUpdate", {
    "text": fields.String(description="Review text"),
    "rating": fields.Integer(description="Rating, 1 to 5"),
})

review_response_model = api.model("ReviewResponse", {
    "id": fields.String(readonly=True, description="Review unique id"),
    "text": fields.String(description="Review text"),
    "rating": fields.Integer(description="Rating, 1 to 5"),
    "place_id": fields.String(description="Place id"),
    "user_id": fields.String(description="User id"),
    "created_at": fields.String(readonly=True, description="Creation timestamp"),
    "updated_at": fields.String(readonly=True, description="Last update timestamp"),
})

message_model = api.model("Message", {
    "message": fields.String(description="Status message"),
})


def serialize_review(review):
    """Return the public API representation of a review."""
    return {
        "id": review.id,
        "text": review.text,
        "rating": review.rating,
        "place_id": review.place.id if hasattr(review, 'place') and review.place else review.place_id,
        "user_id": review.user.id if hasattr(review, 'user') and review.user else review.user_id,
        "created_at": review.created_at.isoformat() if hasattr(review.created_at, 'isoformat') else review.created_at,
        "updated_at": review.updated_at.isoformat() if hasattr(review.updated_at, 'isoformat') else review.updated_at,
    }


@api.route("/")
class ReviewList(Resource):
    """Provide collection-level review operations."""

    @api.marshal_list_with(review_response_model)
    def get(self):
        """List all reviews."""
        return [serialize_review(r) for r in facade.get_all_reviews()]

    @api.expect(review_model, validate=True)
    @api.marshal_with(review_response_model, code=201)
    @api.response(201, "Review successfully created", review_response_model)
    @api.response(400, "Invalid input data")
    @api.response(401, "Missing or invalid token")
    @jwt_required()
    def post(self):
        """Create a new review with ownership and duplication checks."""
        current_user_id = get_jwt_identity()
        data = api.payload

        place_id = data.get("place_id")
        place = facade.get_place(place_id)
        if not place:
            api.abort(404, "Place not found")

        # Prevent owners from reviewing their own places 🚫
        owner_id = place.owner_id if hasattr(place, 'owner_id') else place.owner.id
        if owner_id == current_user_id:
            api.abort(400, "You cannot review your own place")

        # Prevent duplicate reviews from the same user for the same place 🚫
        existing_reviews = facade.get_reviews_by_place(place_id)
        for review in existing_reviews:
            r_user_id = review.user.id if hasattr(review, 'user') and review.user else review.user_id
            if r_user_id == current_user_id:
                api.abort(400, "You have already reviewed this place")

        # Ensure user_id comes from the authenticated token 🔑
        data["user_id"] = current_user_id

        try:
            review = facade.create_review(data)
        except ValueError as e:
            api.abort(400, str(e))
        return serialize_review(review), 201


@api.route("/<string:review_id>")
class ReviewResource(Resource):
    """Provide operations for an individual review."""

    @api.marshal_with(review_response_model)
    @api.response(200, "Review details retrieved successfully", review_response_model)
    @api.response(404, "Review not found")
    def get(self, review_id):
        """Get a review by ID."""
        review = facade.get_review(review_id)
        if not review:
            api.abort(404, "Review not found")
        return serialize_review(review), 200

    @api.expect(review_update_model, validate=True)
    @api.marshal_with(review_response_model)
    @api.response(200, "Review successfully updated", review_response_model)
    @api.response(401, "Missing or invalid token")
    @api.response(403, "Unauthorized action")
    @api.response(404, "Review not found")
    @api.response(400, "Invalid input data")
    @jwt_required()
    def put(self, review_id):
        """Update a review."""
        current_user_id = get_jwt_identity()
        review = facade.get_review(review_id)
        if not review:
            api.abort(404, "Review not found")

        r_user_id = review.user.id if hasattr(review, 'user') and review.user else review.user_id
        if r_user_id != current_user_id:
            api.abort(403, "Unauthorized action: you can only update your own reviews")

        try:
            updated = facade.update_review(review_id, api.payload)
        except ValueError as e:
            api.abort(400, str(e))
        return serialize_review(updated), 200

    @api.marshal_with(message_model)
    @api.response(200, "Review successfully deleted", message_model)
    @api.response(401, "Missing or invalid token")
    @api.response(403, "Unauthorized action")
    @api.response(404, "Review not found")
    @jwt_required()
    def delete(self, review_id):
        """Delete a review."""
        current_user_id = get_jwt_identity()
        review = facade.get_review(review_id)
        if not review:
            api.abort(404, "Review not found")

        r_user_id = review.user.id if hasattr(review, 'user') and review.user else review.user_id
        if r_user_id != current_user_id:
            api.abort(403, "Unauthorized action: you can only delete your own reviews")

        facade.delete_review(review_id)
        return {"message": "Review deleted successfully"}, 200
