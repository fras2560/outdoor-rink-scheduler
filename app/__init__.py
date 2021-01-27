# -*- coding: utf-8 -*-
"""The main entry into the website"""
from flask import Flask
from app.config import Config
from app.model import DB
from app.authentication import github_blueprint, facebook_blueprint,\
    google_blueprint, login_manager

# initialize the app
APP = Flask(__name__)
APP.config.from_object(Config)

# register the all the blueprints
APP.register_blueprint(github_blueprint, url_prefix="/login")
APP.register_blueprint(facebook_blueprint, url_prefix="/login")
APP.register_blueprint(google_blueprint, url_prefix="/login")


# init DB and login manager
DB.init_app(APP)
login_manager.init_app(APP)

# needs to be imported at end to avoid circular dependency
from app.views import *
from app.error_handling import handle_generic_error
