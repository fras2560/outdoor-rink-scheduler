# -*- coding: utf-8 -*-
"""The main entry into the website"""
import pytest
from app import APP
from initDB import init_database, DB
from app.model import Rink, User
from uuid import uuid1 as uuid
from app.config import TestConfig


@pytest.fixture
def client():
    APP.config.from_object(TestConfig)
    with APP.test_client() as client:
        init_database()
        yield client


@pytest.fixture
def database():
    APP.config.from_object(TestConfig)
    with APP.app_context() :
        init_database()
        yield DB


@pytest.fixture
def some_rink(database):
    rink = Rink(str(uuid()))
    database.session.add(rink)
    database.session.commit()
    assert rink.id is not None
    yield rink


@pytest.fixture
def some_user(database):
    user = User(str(uuid()) + "@gmail.com")
    database.session.add(user)
    database.session.commit()
    assert user.id is not None
    yield user


@pytest.fixture
def some_coordinator(database, some_rink):
    user = User(
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
    user = User(
        str(uuid()) + "@gmail.com",
        some_rink,
        is_administrator=True,
        is_coordinator=True)
    database.session.add(user)
    database.session.commit()
    assert user.id is not None
    yield user
