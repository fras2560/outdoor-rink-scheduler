# -*- coding: utf-8 -*-
"""holds views of static pages."""
from flask import render_template
from app import APP


@APP.route("/about")
def about_page():
    return render_template("about.html",
                           page="page",
                           title="About the app")
