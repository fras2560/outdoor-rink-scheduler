# -*- coding: utf-8 -*-
"""Holds configuration for the app."""
import os
from uuid import uuid1


class Config(object):
    URL = os.environ.get("DATABASE_URL", "sqlite://")
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "sqlite://")
    SECRET_KEY = os.environ.get("SECRET_KEY", str(uuid1()))
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "sqlite://")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    USE_SESSION_FOR_NEXT = True
    TESTING = os.environ.get("TESTING", False)
    DEBUG = os.environ.get("DEBUG", False)
    COVID_LOCKDOWN = os.environ.get("COVID", False)
    GOOGLE_OAUTH_CLIENT_ID = os.environ.get("GOOGLE_OAUTH_CLIENT_ID", "")
    GOOGLE_OAUTH_CLIENT_SECRET = os.environ.get(
        "GOOGLE_OAUTH_CLIENT_SECRET", "")
    FACEBOOK_OAUTH_CLIENT_ID = os.environ.get("FACEBOOK_OAUTH_CLIENT_ID", "")
    FACEBOOK_OAUTH_CLIENT_SECRET = os.environ.get(
        "FACEBOOK_OAUTH_CLIENT_SECRET", "")
    GITHUB_OAUTH_CLIENT_ID = os.environ.get("GITHUB_OAUTH_CLIENT_ID", "")
    GITHUB_OAUTH_CLIENT_SECRET = os.environ.get(
        "GITHUB_OAUTH_CLIENT_SECRET", "")
    USE_SESSION_FOR_NEXT = True
    MAX_BOOKINGS_PER_DAY = os.environ.get("MAX_BOOKINGS", 3)
    TIMEZONE = os.environ.get("TIMEZONE", "America/New_York")


class TestConfig(object):
    URL = "sqlite://"
    SQLALCHEMY_DATABASE_URI = "sqlite://"
    SECRET_KEY = str(uuid1())
    SQLALCHEMY_DATABASE_URI = "sqlite://"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    USE_SESSION_FOR_NEXT = True
    TESTING = True
    DEBUG = True
    COVID_LOCKDOWN = True
    GOOGLE_OAUTH_CLIENT_ID = ""
    GOOGLE_OAUTH_CLIENT_SECRET = ""
    FACEBOOK_OAUTH_CLIENT_ID = ""
    FACEBOOK_OAUTH_CLIENT_SECRET = ""
    GITHUB_OAUTH_CLIENT_ID = ""
    GITHUB_OAUTH_CLIENT_SECRET = ""
    USE_SESSION_FOR_NEXT = True
    MAX_BOOKINGS_PER_DAY = os.environ.get("MAX_BOOKINGS", 3)
    TIMEZONE = os.environ.get("TIMEZONE", "America/New_York")
