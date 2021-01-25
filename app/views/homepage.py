# -*- coding: utf-8 -*-
"""Holds views for the homepage and its APIs."""
from flask import render_template
from app import APP
from app.model import Rink


@APP.route("/")
def homepage():
    rinks = Rink.query.all()
    return render_template("homepage.html", rinks=rinks)
