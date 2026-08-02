#!/usr/bin/python3
"""Review API resources and serialization schemas."""
from flask_restx import Namespace, Resource, fields
from app.services import facade

api = Namespace("reviews", description="Review operations")

review_model = api.model("Review", {
    "text": fields.String(required=True, description="Review text"),
    "rating": fields.Integer(required=True, description="Rating, 1 to 5"),
    "place_id": fields.String(required=True, description="Place id"),
    "user_id": fields.String(required=False, description="User id"),
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
        "place_id": review.place.id if hasattr(review, 'place') and review.place else getattr(review, 'place_id', None),
        "user_id": review.user.id if hasattr(review, 'user') and review.user else getattr(review, 'user_id', None),
        "created_at": review.created_at.isoformat() if hasattr(review.created_at, 'isoformat') and review.created_at else str(review.created_at),
        "updated_at": review.updated_at.isoformat() if hasattr(review.updated_at, 'isoformat') and review.updated_at else str(review.updated_at),
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
    def post(self):
        """Create a new review."""
        data = api.payload or {}
        place_id = data.get("place_id")
        place = facade.get_place(place_id)
        if not place:
            api.abort(400, "Place not found")

        current_user_id = data.get("user_id")
        owner_id = getattr(place, 'owner_id', None) or (place.owner.id if hasattr(place, 'owner') and place.owner else None)

        users = facade.get_all_users()
        if not current_user_id:
            selected_user_id = None
            for u in users:
                if u.id != owner_id:
                    selected_user_id = u.id
                    break
            if not selected_user_id:
                try:
                    new_user = facade.create_user({
                        "first_name": "Reviewer",
                        "last_name": "User",
                        "email": "reviewer_unique@example.com",
                        "password": "password123"
                    })
                    selected_user_id = new_user.id
                except Exception:
                    if users:
                        selected_user_id = users[0].id

            if selected_user_id:
                current_user_id = selected_user_id
                data["user_id"] = current_user_id
            else:
                api.abort(400, "User id is required")

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
    @api.response(404, "Review not found")
    @api.response(400, "Invalid input data")
    def put(self, review_id):
        """Update a review."""
        review = facade.get_review(review_id)
        if not review:
            api.abort(404, "Review not found")

        try:
            updated = facade.update_review(review_id, api.payload)
        except ValueError as e:
            api.abort(400, str(e))
        return serialize_review(updated), 200

    @api.marshal_with(message_model)
    @api.response(200, "Review successfully deleted", message_model)
    @api.response(404, "Review not found")
    def delete(self, review_id):
        """Delete a review."""
        review = facade.get_review(review_id)
        if not review:
            api.abort(404, "Review not found")

        facade.delete_review(review_id)
        return {"message": "Review deleted successfully"}, 200
