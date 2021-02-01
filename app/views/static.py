# -*- coding: utf-8 -*-
"""holds views of static pages."""
from flask import render_template, current_app


@current_app.route("/about")
def about_page():
    return render_template("about.html",
                           page="page",
                           title="About the app")


@current_app.route("/privacy")
def privacy_policy():
    """A route for the privacy policy."""
    return render_template("privacy_policy.html")


@current_app.route("/terms-and-conditions")
def terms_and_conditions():
    """A route for the terms and conditions."""
    return render_template("terms_and_conditions.html")
