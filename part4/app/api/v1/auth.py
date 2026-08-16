#!/usr/bin/python3
"""Authentication module for JWT login."""

from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import create_access_token
from app import bcrypt
from app.services import facade

api = Namespace('auth', description='Authentication operations')

# Hashed once at import time and checked on every login where the email
# isn't found, so a failed login takes the same time either way. Without
# this, verify_password() (bcrypt, deliberately slow) only runs when the
# user exists, and the timing difference lets an attacker tell which
# emails are registered without ever guessing a password.
_DUMMY_HASH = bcrypt.generate_password_hash(
    'dummy-password-for-timing-safety'
).decode('utf-8')

# Model for input validation
login_model = api.model('Login', {
    'email': fields.String(required=True, description='User email'),
    'password': fields.String(required=True, description='User password')
})


@api.route('/login')
class Login(Resource):
    @api.expect(login_model, validate=True)
    @api.response(200, 'Login successful')
    @api.response(400, 'Invalid input data')
    @api.response(401, 'Invalid credentials')
    def post(self):
        """Authenticate user and return a JWT token"""
        credentials = api.payload or {}  # Get the email and password from the request payload

        # Step 1: Retrieve the user based on the provided email
        user = facade.get_user_by_email(credentials.get('email'))
        password = credentials.get('password', '')

        # Step 2: Check if the user exists and the password is correct.
        # Always run a bcrypt check, even for an unknown email, so this
        # takes the same time in both cases (see _DUMMY_HASH above).
        if user:
            password_ok = user.verify_password(password)
        else:
            bcrypt.check_password_hash(_DUMMY_HASH, password)
            password_ok = False

        if not user or not password_ok:
            return {'error': 'Invalid credentials'}, 401

        # Step 3: Create a JWT token with the user's id and is_admin flag
        access_token = create_access_token(
            identity=str(user.id),   # only user ID goes here
            additional_claims={"is_admin": user.is_admin}  # extra info here
        )

        # Step 4: Return the JWT token to the client
        return {'access_token': access_token}, 200
