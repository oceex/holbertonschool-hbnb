#!/usr/bin/python3
"""Shared authentication helpers for the API test suite.

``POST /api/v1/users/`` is admin-only, which means there is no way to
create the *first* user through the API itself -- exactly like a real
deployment, which solves this with the fixed administrator inserted by
``sql/seed.sql``. These helpers solve it the same way for tests: seed one
throwaway admin directly through the facade, then use that admin's JWT to
create further users through the real endpoint.
"""
import uuid

from run import app
from app.services import facade


def auth_header(client, email, password):
    """Log in through POST /auth/login and return a Bearer auth header."""
    response = client.post(
        '/api/v1/auth/login',
        json={'email': email, 'password': password},
    )
    assert response.status_code == 200, response.get_json()
    token = response.get_json()['access_token']
    return {'Authorization': f'Bearer {token}'}


def make_admin(client):
    """Seed an admin (bypassing the admin-only endpoint) and log them in.

    Returns (user_dict, headers).
    """
    email = f"admin_{uuid.uuid4()}@test.com"
    password = "adminpass123"
    with app.app_context():
        admin = facade.create_user({
            "first_name": "Admin",
            "last_name": "User",
            "email": email,
            "password": password,
            "is_admin": True,
        })
        admin_id = admin.id
    return {"id": admin_id, "email": email}, auth_header(client, email, password)


def make_user(client, admin_headers, **overrides):
    """Create a regular user through the real POST /users/ endpoint.

    Requires an admin's auth header, since user creation is admin-only.
    Returns (user_dict, headers) for the newly created (non-admin) user.
    """
    payload = {
        "first_name": "Test",
        "last_name": "User",
        "email": f"user_{uuid.uuid4()}@test.com",
        "password": "password123",
    }
    payload.update(overrides)
    response = client.post(
        '/api/v1/users/',
        json=payload,
        headers=admin_headers,
    )
    assert response.status_code == 201, response.get_json()
    user = response.get_json()
    return user, auth_header(client, payload['email'], payload['password'])
