# -*- coding: utf-8 -*-
"""Holds views and API related to the rink page."""
from flask import render_template
from app import APP
from app.model import Rink
from app.errors import NotFoundException


@APP.route("/rink/<int:rink_id>")
def rink_page(rink_id):
    rink = Rink.query.get(rink_id)
    if rink is None:
        raise NotFoundException(f"Sorry, rink not found - {rink_id}")
    return render_template("rink.html", rink=rink)
