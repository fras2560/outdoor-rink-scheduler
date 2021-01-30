# -*- coding: utf-8 -*-
"""Holds views that are only used for testing."""
from flask import Response, request, current_app
from flask_login import login_user
from functools import wraps
from app.model import People, DB
from app.logging import LOGGER
import json


def requires_testing(f):
    """A decorator for routes that only available while testing"""
    @wraps(f)
    def decorated(*args, **kwargs):
        are_testing = current_app.config['TESTING']
        if are_testing is None or not are_testing:
            return Response("Testing feature not on", 400)
        return f(*args, **kwargs)
    return decorated


@current_app.route("/testing/api/login", methods=["POST"])
@requires_testing
def create_and_login():
    user_info = request.get_json(silent=True)
    coordinator = (user_info.get("is_coordinator", False) or
                   user_info.get("isCoordinator", False))
    admin = (user_info.get("is_administrator", False) or
             user_info.get("isAdministrator", False))
    user = People.query.filter(
        People.email == user_info.get('email')).first()
    if user is None:
        LOGGER.info(f"Adding person: {user_info}")
        user = People(user_info.get("email"),
                      is_coordinator=coordinator,
                      is_administrator=admin)
        DB.session.add(user)
        DB.session.commit()
    else:
        LOGGER.info(f"Logged in existing user: {user_info}")
    login_user(user)
    return Response(json.dumps(user.json()), 200)
