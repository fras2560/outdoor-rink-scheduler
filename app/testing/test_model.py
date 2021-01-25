# -*- coding: utf-8 -*-
"""Testing various methods for the model"""
from app.testing import client, database, some_rink, some_user
from app.model import Rink, Status, Booking
from uuid import uuid1 as uuid
from initDB import MOCK_DATA
from dateutil import tz
from datetime import datetime, timedelta


EST = tz.gettz('America/New_York')
TODAY = datetime.utcnow().date()
TODAY_AT_NOON =  datetime(TODAY.year, TODAY.month, TODAY.day, hour=12,
                          minute=0, tzinfo=tz.tzutc()).astimezone(EST)
YESTERDAY_AT_NOON =  TODAY_AT_NOON - timedelta(days=1)
TOMORROW_AT_NOON =  TODAY_AT_NOON + timedelta(days=1)

def test_rink_model(database):
    # test able to handle no status
    name = str(uuid())
    rink = Rink(name)
    database.session.add(rink)
    database.session.commit()
    assert rink.id is not None
    assert rink.name == name
    assert rink.json() is not None
    assert str(rink) is not None

def test_get_current_status(database, some_rink):
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

def test_today_booking(database, some_rink, some_user):
    # a booking yesterday, today and tomorrow
    yesterday_booking = Booking(some_user, some_rink, YESTERDAY_AT_NOON)
    today_booking = Booking(some_user, some_rink, TODAY_AT_NOON)
    tomorrow_booking = Booking(some_user, some_rink, TOMORROW_AT_NOON)
    database.session.add(yesterday_booking)
    database.session.add(today_booking)
    database.session.add(tomorrow_booking)
    database.session.commit()

    # ensure today book only one that is returned
    bookings = some_rink.today_bookings()
    assert len(bookings) == 1
    assert bookings[0].id == today_booking.id
    assert bookings[0].json() is not None
