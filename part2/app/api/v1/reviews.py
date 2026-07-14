#!/usr/bin/python3
"""Reviews API namespace: /api/v1/reviews/"""
from flask_restx import Namespace, Resource, fields

from app.services import facade

api = Namespace("reviews", description="Review operations")

# -- Request (input) models ----------------------------------------------
review_model = api.model("Review", {
    "text": fields.String(required=True, description="Review text"),
    "rating": fields.Integer(required=True,
                              description="Rating, 1 to 5"),
    "place_id": fields.String(required=True, description="Place id"),
    "user_id": fields.String(required=True, description="User id"),
})

review_update_model = api.model("ReviewUpdate", {
    "text": fields.String(description="Review text"),
    "rating": fields.Integer(description="Rating, 1 to 5"),
})

# -- Response (output) model ----------------------------------------------
review_response_model = api.model("ReviewResponse", {
    "id": fields.String(readonly=True, description="Review unique id"),
    "text": fields.String(description="Review text"),
    "rating": fields.Integer(description="Rating, 1 to 5"),
    "place_id": fields.String(description="Place id"),
    "user_id": fields.String(description="User id"),
    "created_at": fields.String(readonly=True,
                                 description="Creation timestamp"),
    "updated_at": fields.String(readonly=True,
                                 description="Last update timestamp"),
})

message_model = api.model("Message", {
    "message": fields.String(description="Status message"),
})


def serialize_review(review):
    return {
        "id": review.id,
        "text": review.text,
        "rating": review.rating,
        "place_id": review.place.id,
        "user_id": review.user.id,
        "created_at": review.created_at.isoformat(),
        "updated_at": review.updated_at.isoformat(),
    }


@api.route("/")
class ReviewList(Resource):
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
        try:
            review = facade.create_review(api.payload)
        except ValueError as e:
            api.abort(400, str(e))
        return serialize_review(review), 201


@api.route("/<string:review_id>")
class ReviewResource(Resource):
    @api.marshal_with(review_response_model)
    @api.response(200, "Review details retrieved successfully",
                  review_response_model)
    @api.response(404, "Review not found")
    def get(self, review_id):
        """Get a review by id."""
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
        if not facade.get_review(review_id):
            api.abort(404, "Review not found")
        facade.delete_review(review_id)
        return {"message": "Review deleted successfully"}, 200
