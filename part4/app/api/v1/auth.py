#!/usr/bin/python3
"""Authentication module for JWT login."""

from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import create_access_token
from app import bcrypt
from app.services import facade

api = Namespace('auth', description='Authentication operations')

# Compared against whenever the email is unknown, so a failed login costs the
# same either way. Otherwise the response time alone would reveal which email
# addresses are registered.
_DUMMY_HASH = bcrypt.generate_password_hash(
    'dummy-password-for-timing-safety'
).decode('utf-8')

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
        credentials = api.payload or {}
        user = facade.get_user_by_email(credentials.get('email'))
        password = credentials.get('password', '')

        # A hash is always compared, even for an unknown email, so both
        # outcomes take the same time.
        if user:
            password_ok = user.verify_password(password)
        else:
            bcrypt.check_password_hash(_DUMMY_HASH, password)
            password_ok = False

        if not user or not password_ok:
            return {'error': 'Invalid credentials'}, 401

        # The role travels as a claim so protected endpoints can authorise a
        # request without loading the user again.
        access_token = create_access_token(
            identity=str(user.id),
            additional_claims={"is_admin": user.is_admin}
        )

        return {'access_token': access_token}, 200
