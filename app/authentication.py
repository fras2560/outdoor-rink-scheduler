# -*- coding: utf-8 -*-
"""Holds authenication a user using OAuth providers."""

from typing import TypedDict
from functools import wraps
from flask import Blueprint, Response
from flask_dance.contrib.github import make_github_blueprint
from flask_dance.contrib.facebook import make_facebook_blueprint
from flask_dance.contrib.google import make_google_blueprint
from flask_dance.consumer.storage.sqla import SQLAlchemyStorage
from flask_dance.consumer import oauth_authorized, oauth_error
from flask_login import LoginManager, current_user, login_user
from sqlalchemy.orm.exc import NoResultFound
from app.errors import OAuthException
from app.model import DB, OAuth, People
from app.logging import LOGGER
import os


login_manager = LoginManager()
login_manager.login_view = "loginpage"

github_blueprint = make_github_blueprint(
    scope=["email"],
    storage=SQLAlchemyStorage(OAuth, DB.session, user=current_user)
)
facebook_blueprint = make_facebook_blueprint(
    scope=["email"],
    storage=SQLAlchemyStorage(OAuth, DB.session, user=current_user))
google_blueprint = make_google_blueprint(
    scope=["profile", "email"],
    storage=SQLAlchemyStorage(OAuth, DB.session, user=current_user))
FACEBOOK = "facebook"
GOOGLE = "google"
GITHUB = "github"


class UserInfo(TypedDict):
    """The required user info from a ouath provider"""
    name: str
    email: str


@oauth_authorized.connect_via(facebook_blueprint)
@oauth_authorized.connect_via(github_blueprint)
@oauth_authorized.connect_via(google_blueprint)
def oauth_service_provider_logged_in(blueprint: Blueprint, token: str) -> bool:
    """The handler for dealing when OAuth has logged someone in correctly

    Args:
        blueprint (Blueprint): the OAuth provider they logged into
        token (str): the token received from provider

    Raises:
        OAuthException: when missing vital information like token or email
        HaveLeagueRequestException: when they have already request to join

    Returns:
        bool: False - Disable Flask-Dance's default behavior for saving
                      the OAuth token
    """
    # ensure the token is correct
    if not token:
        LOGGER.warning(f"{blueprint.name} did not send token: {token}")
        raise OAuthException("Failed to log in")

    # get the user info
    user_info = get_user_info(blueprint)
    user_id = user_info["id"]

    # user info to lookup oauth
    oauth = get_oauth(blueprint.name, user_id, token)
    if oauth.user:
        login_user(oauth.user)
        LOGGER.info(f"{oauth.user} signed in")
    else:
        # see email already used
        user = People.query.filter(
            People.email.ilike(user_info.get('email'))).one()
        if user is None:
            user = People(user_info.get('email'))
        # associated the player with this oauth
        oauth.user = user
        DB.session.add(user)
        DB.session.add(oauth)
        DB.session.commit()
        LOGGER.info(f"{user} has joined the app")
        login_user(user)
    # Disable Flask-Dance's default behavior for saving the OAuth token
    return False


@oauth_error.connect_via(facebook_blueprint)
def oauth_service_provider_error(blueprint: Blueprint,
                                 message: str,
                                 response: dict):
    """Got an error from the OAuth service provider

    Args:
        blueprint (Blueprint): the OAuth service provider
        message (str): the message from the provider
        response (dict): the response from the provider

    Raises:
        OAuthException: the exceptionr raised to be dealt with by application
    """
    msg = f"{blueprint.name}! message={message} response={response}"
    LOGGER.error(msg)
    raise OAuthException(msg)


@login_manager.user_loader
def load_user(user_id: int) -> People:
    """Loads the logged in user based upon their id."""
    return People.query.get(int(user_id))


def get_oauth(name: str, user_id: str, token: str) -> OAuth:
    """Get the oauth associated with the given user id and oauth provider.

    Args:
        name (str): the name of the oauth provider
        user_id (str): the id of the user according to oauth provider
        token (str): the oauth token

    Returns:
        OAuth: the oauth that we have saved or newly created one
    """
    # Find this OAuth token in the database, or create it
    user_id = str(user_id)
    query = OAuth.query.filter_by(provider=name, provider_user_id=user_id)
    try:
        oauth = query.one()
    except NoResultFound:
        oauth = OAuth(provider=name, provider_user_id=user_id, token=token)
    return oauth


def get_user_info(blueprint: Blueprint) -> UserInfo:
    """Get the user info from the oauth provider.

    Args:
        blueprint (Blueprint): the oauth provider blueprint

    Raises:
        OAuthException: Unsupported blueprint or unable to get user info

    Returns:
        UserInfo: the user info
    """
    resp = None
    if blueprint.name == FACEBOOK:
        resp = blueprint.session.get("/me?fields=id,email")
    elif blueprint.name == GOOGLE:
        resp = blueprint.session.get("/oauth2/v1/userinfo")
    elif blueprint.name == GITHUB:
        resp = blueprint.session.get("user")
    if resp is None:
        LOGGER.error(f"Unsupported oauth blueprint: {blueprint.name}")
        raise OAuthException(f"Unsupported oauth blueprint: {blueprint.name}")
    if not resp.ok:
        LOGGER.error(resp)
        LOGGER.error(f"Unable to fetch user using {blueprint.name}")
        raise OAuthException(
            f"Failed to get user info oauth blueprint: {blueprint.name}")
    user_info = resp.json()
    if user_info.get("email") is None:
        msg = (
            f"Provider did not give email: {blueprint.name}."
            " Double check your permission from the app."
            " If using Github ensure your email is public."
        )
        LOGGER.error(msg)
        LOGGER.error(user_info)
        raise OAuthException(msg)
    return user_info


def are_logged_in() -> bool:
    """Returns whether the person is logged in."""
    return current_user.get_id() is not None


def get_login_email() -> str:
    """Returns the email based whichever app they have authorized with."""
    return None if not are_logged_in() else current_user.email


def is_gmail_supported() -> bool:
    """Returns whether current setup support Gmail authentication."""
    return os.environ.get("GOOGLE_OAUTH_CLIENT_ID", "") != ""


def is_github_supported() -> bool:
    """Returns whether current setup support Github authentication."""
    return os.environ.get("GITHUB_OAUTH_CLIENT_ID", "") != ""


def is_facebook_supported() -> bool:
    """Returns whether current setup support Facebook authentication."""
    return os.environ.get("FACEBOOK_OAUTH_CLIENT_ID", "") != ""


def api_user_required(f):
    """A decorator for APIs that require a logged-in user."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if not are_logged_in():
            return Response("API requires logged-in user", 401)
        return f(*args, **kwargs)
    return decorated


def api_admin_required(f):
    """A decorator for APIs that require a player with score permissions ."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if not are_logged_in() or not current_user.is_administrator:
            return Response("API requires a player with score permission", 401)
        return f(*args, **kwargs)
    return decorated


def api_coordinator_required(f):
    """A decorator for APIs that require a player with score permissions ."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if (not are_logged_in() or
                (not current_user.is_administrator and
                    not current_user.is_coordinator)):
            return Response("API requires user to be coordinator or admin",
                            401)
        return f(*args, **kwargs)
    return decorated
