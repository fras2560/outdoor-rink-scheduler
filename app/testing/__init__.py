# -*- coding: utf-8 -*-
"""The main entry into the website"""
from app.config import TestConfig
from app.helpers import get_time_today
from app.model import Rink, People, Status, DB
from app import APP
from datetime import timedelta
from initDB import init_database
from uuid import uuid1 as uuid
import pytest


NON_EXISTENT = 10000000000000


@pytest.fixture
def client():
    APP.config.from_object(TestConfig)
    with APP.test_client() as client:
        init_database()
        yield client


@pytest.fixture
def today_at_noon(client):
    yield get_time_today(12, minute=0)


@pytest.fixture
def yesterday_at_noon(client, today_at_noon):
    yield today_at_noon - timedelta(days=1)


@pytest.fixture
def tomorrow_at_noon(client, today_at_noon):
    yield today_at_noon - timedelta(days=1)


@pytest.fixture
def database():
    APP.config.from_object(TestConfig)
    with APP.app_context():
        init_database()
        yield DB


@pytest.fixture
def open_rink(database, some_rink):
    status = Status(some_rink, True, "Open",
                    description="rink open for the season")
    database.session.add(status)
    database.session.commit()
    assert status.id is not None
    yield some_rink


@pytest.fixture
def closed_rink(database, some_rink):
    status = Status(some_rink, False, "Closed",
                    description="rink closed for the season")
    database.session.add(status)
    database.session.commit()
    assert status.id is not None
    yield some_rink


@pytest.fixture
def some_rink(database):
    rink = Rink(str(uuid()))
    database.session.add(rink)
    database.session.commit()
    assert rink.id is not None
    yield rink


@pytest.fixture
def some_user(database):
    user = People(str(uuid()) + "@gmail.com")
    database.session.add(user)
    database.session.commit()
    assert user.id is not None
    yield user


@pytest.fixture
def some_coordinator(database, some_rink):
    user = People(
        str(uuid()) + "@gmail.com",
        some_rink,
        is_administrator=False,
        is_coordinator=True)
    database.session.add(user)
    database.session.commit()
    assert user.id is not None
    yield user


@pytest.fixture
def some_administrator(database, some_rink):
    user = People(
        str(uuid()) + "@gmail.com",
        some_rink,
        is_administrator=True,
        is_coordinator=True)
    database.session.add(user)
    database.session.commit()
    assert user.id is not None
    yield user
