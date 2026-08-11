#!/usr/bin/python3
"""User API resources and serialization schemas."""
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt

from app.services import facade


def current_user_is_admin():
    """Return whether the caller's JWT carries an is_admin=True claim."""
    return get_jwt().get("is_admin", False)


api = Namespace("users", description="User operations")

user_model = api.model("User", {
    "first_name": fields.String(required=True, description="First name", max_length=50),
    "last_name": fields.String(required=True, description="Last name", max_length=50),
    "email": fields.String(required=True, description="Email address"),
    "password": fields.String(required=True, description="User password"),
    "is_admin": fields.Boolean(description="Administrator flag", default=False),
})

user_update_model = api.model("UserUpdate", {
    "first_name": fields.String(description="First name", max_length=50),
    "last_name": fields.String(description="Last name", max_length=50),
    "email": fields.String(description="Email address"),
    "password": fields.String(description="User password"),
    "is_admin": fields.Boolean(description="Administrator flag"),
})

user_response_model = api.model("UserResponse", {
    "id": fields.String(readonly=True, description="User unique id"),
    "first_name": fields.String(description="First name"),
    "last_name": fields.String(description="Last name"),
    "email": fields.String(description="Email address"),
    "is_admin": fields.Boolean(description="Administrator flag"),
    "created_at": fields.String(readonly=True, description="Creation timestamp"),
    "updated_at": fields.String(readonly=True, description="Last update timestamp"),
})


def serialize_user(user):
    """Return the public API representation of a user."""
    return {
        "id": user.id,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "email": user.email,
        "is_admin": user.is_admin,
        "created_at": user.created_at.isoformat() if hasattr(user.created_at, 'isoformat') else user.created_at,
        "updated_at": user.updated_at.isoformat() if hasattr(user.updated_at, 'isoformat') else user.updated_at,
    }


@api.route("/")
class UserList(Resource):
    """Provide collection-level user operations."""

    @api.marshal_list_with(user_response_model)
    def get(self):
        """List all users."""
        return [serialize_user(u) for u in facade.get_all_users()]

    @jwt_required()
    @api.expect(user_model, validate=True)
    @api.marshal_with(user_response_model, code=201)
    @api.response(201, "User successfully created", user_response_model)
    @api.response(400, "Invalid input data")
    @api.response(403, "Admin privileges required")
    def post(self):
        """Create a new user (admin only)."""
        if not current_user_is_admin():
            api.abort(403, "Admin privileges required")

        try:
            user = facade.create_user(api.payload)
        except ValueError as e:
            api.abort(400, str(e))
        return serialize_user(user), 201


@api.route("/<string:user_id>")
class UserResource(Resource):
    """Provide operations for an individual user."""

    @api.marshal_with(user_response_model)
    @api.response(200, "User details retrieved successfully", user_response_model)
    @api.response(404, "User not found")
    def get(self, user_id):
        """Get a user by ID."""
        user = facade.get_user(user_id)
        if not user:
            api.abort(404, "User not found")
        return serialize_user(user), 200

    @jwt_required()
    @api.expect(user_update_model, validate=True)
    @api.marshal_with(user_response_model)
    @api.response(200, "User successfully updated", user_response_model)
    @api.response(403, "Not authorized to modify this user")
    @api.response(404, "User not found")
    @api.response(400, "Invalid input data")
    def put(self, user_id):
        """Update a user's information.

        A regular user may update only their own first/last name. Only an
        admin may change email, password, or is_admin -- and may do so for
        any user, not just themselves.
        """
        user = facade.get_user(user_id)
        if not user:
            api.abort(404, "User not found")

        is_self = get_jwt_identity() == user_id
        is_admin = current_user_is_admin()

        if not is_self and not is_admin:
            api.abort(403, "Unauthorized action")

        data = api.payload or {}

        if not is_admin:
            if "email" in data or "password" in data:
                api.abort(400, "You cannot modify email or password")
            if "is_admin" in data:
                api.abort(400, "You cannot modify is_admin")

        try:
            updated = facade.update_user(user_id, data)
        except ValueError as e:
            api.abort(400, str(e))
        return serialize_user(updated), 200
