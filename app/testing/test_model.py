# -*- coding: utf-8 -*-
"""Testing various methods for the model"""
from app.testing import client, database, some_rink, some_user,\
    today_at_noon, tomorrow_at_noon, yesterday_at_noon
from app.model import Rink, Status, Booking, have_booked_already
from datetime import datetime
from uuid import uuid1 as uuid


def test_rink_model(client, database, some_rink):
    # test able to handle no status
    assert some_rink.id is not None
    assert some_rink.name is not None
    assert some_rink.json() is not None
    assert str(some_rink) is not None


def test_get_rink_timeslots(client, database, some_rink, some_user,
                            today_at_noon):
    # test timeslots
    timeslots = some_rink.today_timeslots()
    for timeslot in timeslots:
        assert timeslot['booked'] is False

    # book up one of the timeslots
    some_rink.capacity = 1
    today_booking = Booking(some_user, some_rink, today_at_noon)
    database.session.add(today_booking)
    database.session.commit()

    # noon is booked
    timeslots = some_rink.today_timeslots()
    assert timeslots[4]['booked'] is True


def test_get_current_status(client, database, some_rink):
    # test able to handle no status
    assert some_rink.current_status() is None

    # add an original status
    initial_status = Status(some_rink, True, "Grand opening")
    database.session.add(initial_status)
    database.session.commit()
    assert some_rink.current_status() is not None
    assert some_rink.current_status().open is True
    assert some_rink.current_status().state == "Grand opening"
    assert some_rink.current_status().json() is not None
    assert str(some_rink.current_status()) is not None

    # add a new status
    initial_status.end_date = datetime.now()
    new_status = Status(some_rink, False, "Freezing rain storm")
    database.session.add(new_status)
    database.session.commit()
    assert some_rink.current_status() is not None
    assert some_rink.current_status().open is False
    assert some_rink.current_status().state == "Freezing rain storm"
    assert some_rink.current_status().json() is not None
    assert str(some_rink.current_status()) is not None


def test_today_booking(client, database, some_rink, some_user,
                       yesterday_at_noon, today_at_noon, tomorrow_at_noon):
    # a booking yesterday, today and tomorrow
    yesterday_booking = Booking(some_user, some_rink, yesterday_at_noon)
    today_booking = Booking(some_user, some_rink, today_at_noon)
    tomorrow_booking = Booking(some_user, some_rink, tomorrow_at_noon)
    database.session.add(yesterday_booking)
    database.session.add(today_booking)
    database.session.add(tomorrow_booking)
    database.session.commit()

    # ensure today book only one that is returned
    bookings = some_rink.today_bookings()
    assert len(bookings) == 1
    assert bookings[0].id == today_booking.id
    assert bookings[0].json() is not None


def test_have_booked_already(client, database, some_rink, some_user,
                             today_at_noon):
    booking = Booking(some_user, some_rink, today_at_noon)
    assert have_booked_already([booking], 1) is False
    assert have_booked_already([booking], 12) is True
