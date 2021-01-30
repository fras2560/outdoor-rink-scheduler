# -*- coding: utf-8 -*-
"""Holds views for the homepage and its APIs."""
from flask import render_template, session, redirect, current_app
from app.model import Rink


@current_app.route("/")
def homepage():
    next_page = session.get("next", None)
    if next_page is not None:
        # remove it so can return to homepage again
        session.pop("next")
        return redirect(next_page)
    rinks = Rink.query.all()
    return render_template("homepage.html", rinks=rinks)
