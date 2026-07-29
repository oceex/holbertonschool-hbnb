#!/usr/bin/python3
"""User API resources and serialization schemas."""
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.services import facade

api = Namespace("users", description="User operations")

user_model = api.model("User", {
    "first_name": fields.String(required=True, description="First name",
                                 max_length=50),
    "last_name": fields.String(required=True, description="Last name",
                                max_length=50),
    "email": fields.String(required=True, description="Email address"),
    "password": fields.String(required=True, description="User password"),
    "is_admin": fields.Boolean(description="Administrator flag",
                                default=False),
})

user_update_model = api.model("UserUpdate", {
    "first_name": fields.String(description="First name", max_length=50),
    "last_name": fields.String(description="Last name", max_length=50),
    "is_admin": fields.Boolean(description="Administrator flag"),
})

user_response_model = api.model("UserResponse", {
    "id": fields.String(readonly=True, description="User unique id"),
    "first_name": fields.String(description="First name"),
    "last_name": fields.String(description="Last name"),
    "email": fields.String(description="Email address"),
    "is_admin": fields.Boolean(description="Administrator flag"),
    "created_at": fields.String(readonly=True,
                                 description="Creation timestamp"),
    "updated_at": fields.String(readonly=True,
                                 description="Last update timestamp"),
})


def serialize_user(user):
    """Return the public API representation of a user."""
    return {
        "id": user.id,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "email": user.email,
        "is_admin": user.is_admin,
        "created_at": user.created_at.isoformat(),
        "updated_at": user.updated_at.isoformat(),
    }


@api.route("/")
class UserList(Resource):
    """Provide collection-level user operations."""

    @api.marshal_list_with(user_response_model)
    def get(self):
        """List all users."""
        return [serialize_user(u) for u in facade.get_all_users()]

    @api.expect(user_model, validate=True)
    @api.marshal_with(user_response_model, code=201)
    @api.response(201, "User successfully created", user_response_model)
    @api.response(400, "Invalid input data")
    def post(self):
        """Create a new user."""
        data = api.payload
        if facade.get_user_by_email(data.get("email")):
            api.abort(400, "Email already registered")
        try:
            user = facade.create_user(data)
        except ValueError as e:
            api.abort(400, str(e))
        return serialize_user(user), 201


@api.route("/<string:user_id>")
class UserResource(Resource):
    """Provide operations for an individual user."""

    @api.marshal_with(user_response_model)
    @api.response(200, "User details retrieved successfully",
                  user_response_model)
    @api.response(404, "User not found")
    def get(self, user_id):
        """Get a user by ID."""
        user = facade.get_user(user_id)
        if not user:
            api.abort(404, "User not found")
        return serialize_user(user), 200

    @api.expect(user_update_model, validate=True)
    @api.marshal_with(user_response_model)
    @api.response(200, "User successfully updated", user_response_model)
    @api.response(401, "Missing or invalid token")
    @api.response(403, "Unauthorized action")
    @api.response(404, "User not found")
    @api.response(400, "Invalid input data")
    @jwt_required()
    def put(self, user_id):
        """Update a user's information with authorization checks."""
        current_user_id = get_jwt_identity()
        
        # Check if the authenticated user matches the requested user ID
        if current_user_id != user_id:
            api.abort(403, "Unauthorized action")

        data = api.payload
        
        # Prevent modifying email and password
        if "email" in data or "password" in data:
            api.abort(400, "You cannot modify email or password")

        user = facade.get_user(user_id)
        if not user:
            api.abort(404, "User not found")

        try:
            updated = facade.update_user(user_id, data)
        except ValueError as e:
            api.abort(400, str(e))
        return serialize_user(updated), 200
