# -*- coding: utf-8 -*-
"""Testing various rink views and API."""
from app.testing import client, database, some_rink, some_user, closed_rink,\
    open_rink, today_at_noon, tomorrow_at_noon, yesterday_at_noon,\
    NON_EXISTENT
from app.model import Booking, People
from app.config import Config
from app.helpers import get_time_today, loads
from uuid import uuid1 as uuid
import json


def test_non_existent_rink(client):
    """Test rink homepage for non-existent rink."""
    rv = client.get(f"/rink/{NON_EXISTENT}", follow_redirects=True)
    assert b'rink not found' in rv.data


def test_some_rink_anonymous(client, some_rink):
    """Test rink homepage for an anonymous user."""
    # test a non-existent rink
    rv = client.get(f"/rink/{some_rink.id}")
    assert b'Sign in to book' in rv.data
    assert f'{some_rink.name}'.encode() in rv.data


def test_some_rink_logged_in(client, some_rink, some_user):
    """Test rink homepage for a logged in user."""
    client.post("/testing/api/login", data=json.dumps(some_user.json()),
                content_type='application/json')
    rv = client.get(f"/rink/{some_rink.id}")
    assert b'Book an available time today:' in rv.data


def test_some_closed_rink(client, closed_rink, some_user):
    """Test rink homepage for a closed rink."""
    client.post("/testing/api/login", data=json.dumps(some_user.json()),
                content_type='application/json')
    rv = client.get(f"/rink/{closed_rink.id}")
    assert b'Check in later when the rink opens to book a timeslot' in rv.data


def test_some_open_rink(client, open_rink, some_user):
    """Test rink homepage for a open rink."""
    client.post("/testing/api/login", data=json.dumps(some_user.json()),
                content_type='application/json')
    rv = client.get(f"/rink/{open_rink.id}")
    assert b'Book an available time today:' in rv.data


def test_anonymous_user_booking_rink(client, some_rink):
    """Test booking rink as an anonymous user."""
    rv = client.post("/rink/book", data=json.dumps({
        "rink_id": some_rink.id,
        "hour": 12
    }),
        content_type='application/json',)
    assert b'API requires logged-in user' in rv.data
    assert 401 == rv.status_code


def test_user_booking_non_existent(client, some_user):
    """Test booking a non-existent rink."""
    client.post("/testing/api/login", data=json.dumps(some_user.json()),
                content_type='application/json')
    rv = client.post("/rink/book", data=json.dumps({
        "rink_id": NON_EXISTENT,
        "hour": 12
    }),
        content_type='application/json',)
    assert b'Rink not found' in rv.data
    assert 404 == rv.status_code


def test_user_overbooking_rink(client, database, some_rink, some_user,
                               today_at_noon):
    """Test booking a rink that is full."""
    other_user = People(str(uuid()) + "@gmail.com", some_rink,
                        is_administrator=False, is_coordinator=False)
    database.session.add(other_user)
    database.session.add(Booking(other_user, some_rink, today_at_noon))
    some_rink.capacity = 1
    database.session.commit()
    client.post("/testing/api/login", data=json.dumps(some_user.json()),
                content_type='application/json')
    rv = client.post("/rink/book", data=json.dumps({
        "rink_id": some_rink.id,
        "hour": 12
    }),
        content_type='application/json',)
    assert b'Timeslot booked already' in rv.data
    assert 409 == rv.status_code


def test_user_doublebooking_rink(client, database, some_rink, some_user,
                                 today_at_noon):
    """Test booking  same hour at same rink twice."""
    some_rink.capacity = 5
    database.session.add(Booking(some_user, some_rink, today_at_noon))
    database.session.commit()
    client.post("/testing/api/login", data=json.dumps(some_user.json()),
                content_type='application/json')
    rv = client.post("/rink/book", data=json.dumps({
        "rink_id": some_rink.id,
        "hour": 12
    }),
        content_type='application/json',)
    assert b'Have already booked this timeslot' in rv.data
    assert 403 == rv.status_code


def test_user_overbooked_today(client, database, some_rink, some_user,
                               today_at_noon):
    """Test person trying to book too many slots."""
    client.post("/testing/api/login", data=json.dumps(some_user.json()),
                content_type='application/json')
    for hour in range(10, 10 + Config.MAX_BOOKINGS_PER_DAY):
        database.session.add(Booking(some_user, some_rink,
                                     get_time_today(hour)))
        database.session.commit()
    # now book one more
    rv = client.post("/rink/book", data=json.dumps({
        "rink_id": some_rink.id,
        "hour": 21
    }),
        content_type='application/json',)
    assert b'Have booked too many timeslots today' in rv.data
    assert 403 == rv.status_code


def test_successful_booking_rink(client, database, some_rink, some_user,
                                 today_at_noon):
    """Test person successfully booking a rink."""
    client.post("/testing/api/login", data=json.dumps(some_user.json()),
                content_type='application/json')
    rv = client.post("/rink/book", data=json.dumps({
        "rink_id": some_rink.id,
        "hour": 21
    }),
        content_type='application/json',)
    booking = loads(rv.data)
    assert 200 == rv.status_code
    assert booking["rink"]["id"] == some_rink.id
    assert booking["user"]["id"] == some_user.id
    assert booking["hour"] == 21
