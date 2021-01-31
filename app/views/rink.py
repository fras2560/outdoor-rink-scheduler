# -*- coding: utf-8 -*-
"""Holds views and API related to the rink page."""
from flask import render_template, Response, request, session, redirect,\
    url_for, current_app
from flask_login import current_user
from app.model import DB, Rink, Booking, have_booked_already
from app.errors import NotFoundException
from app.authentication import api_user_required, are_logged_in
from app.helpers import get_time_today
from app.config import Config
from dateutil import tz
from datetime import datetime
import json


@current_app.route("/rink/<int:rink_id>")
def rink_page(rink_id):
    """The rink homepage for some rink"""
    rink = Rink.query.get(rink_id)
    if rink is None:
        raise NotFoundException(f"Sorry, rink not found - {rink_id}")
    timeslots = rink.timeslots()

    # check if user has already booked some slots
    if are_logged_in():
        my_bookings = current_user.bookings()
        for i in range(0, len(timeslots)):
            if have_booked_already(my_bookings, timeslots[i]["start"],
                                   end=timeslots[i]["end"]):
                timeslots[i]["user_booked"] = True
    return render_template("rink.html",
                           rink=rink,
                           status=rink.current_status(),
                           timeslots=timeslots)


@ current_app.route("/rink/login/<int:rink_id>")
def rink_redirect_to_login(rink_id):
    """Redirect to login page & back to the given rink after authentication"""
    session['next'] = url_for('rink_page', rink_id=rink_id)
    return redirect(url_for('loginpage'))


@ current_app.route("/rink/book", methods=["POST"])
@ api_user_required
def book_timeslot():
    """Book a timeslot for some rink for some hour"""
    booking_info = request.get_json(silent=True)
    hour = booking_info.get('hour')
    rink_id = booking_info.get('rink_id')
    rink = Rink.query.get(rink_id)
    if rink is None:
        return Response(json.dumps(f"{rink_id}: Rink not found"),
                        status=404, mimetype="application/json")
    rink_timeslot = rink.timeslots(hour=hour)[0]
    my_bookings = current_user.bookings()
    # ensure there is capacity and able to book
    if rink_timeslot['booked']:
        return Response(json.dumps("Timeslot booked already"), 409)
    elif have_booked_already(my_bookings, get_time_today(hour)):
        return Response(json.dumps("Have already booked this timeslot"), 403)
    elif len(my_bookings) >= Config.MAX_BOOKINGS_PER_DAY:
        return Response(json.dumps("Have booked too many timeslots today"),
                        403)
    today = datetime.utcnow().date()
    booking_time = datetime(today.year, today.month, today.day,
                            hour=hour, minute=0,
                            tzinfo=tz.gettz(current_app.config["TIMEZONE"]))
    booking = Booking(current_user, rink, start_date=booking_time)
    DB.session.add(booking)
    DB.session.commit()
    return Response(json.dumps(booking.json()), 200)
