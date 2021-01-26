# -*- coding: utf-8 -*-
"""Holds a database model for the application."""
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import and_
from dateutil import tz
from flask_login import UserMixin
from datetime import datetime, timedelta
from flask_dance.consumer.storage.sqla import OAuthConsumerMixin


"""The database object."""
DB = SQLAlchemy()


class Rink(DB.Model):
    """
        A local KW rink
        Columns:
            id: the unique id
            name: the name of the rink
            capacity: the capacity of the rink
            max_groups: the max number of groups allowed on the rink
            open: the hour the rink open (24 hour time)
            close: the hour the rink closes (24 hour time)
    """
    id = DB.Column(DB.Integer, primary_key=True)
    name = DB.Column(DB.String(256))
    statuses = DB.relationship('Status',
                               backref='statuses', lazy='dynamic')
    bookings = DB.relationship('Booking',
                               backref='bookings', lazy='dynamic')
    coordinators = DB.relationship('User',
                                   backref='coordinators', lazy='dynamic')
    capacity = DB.Column(DB.Integer)
    max_groups = DB.Column(DB.Integer)
    open = DB.Column(DB.Integer)
    close = DB.Column(DB.Integer)

    def __init__(self,
                 name: str,
                 capacity: int = 25,
                 max_groups: int = 25,
                 open: int = 8,
                 close: int = 22):
        self.name = name
        self.capacity = capacity
        self.max_groups = max_groups
        self.open = open
        self.close = close

    def current_status(self) -> 'Status':
        """Returns the current status of the rink"""
        for status in self.statuses:
            if status.end_date is None:
                return status
        return None

    def today_bookings(self) -> list:
        """Returns the booking for the rink today"""
        today = datetime.utcnow().date()
        est = tz.gettz('America/New_York')
        start_of_today = datetime(today.year, today.month, today.day,
                                  tzinfo=tz.tzutc()).astimezone(est)
        end_of_today = start_of_today + timedelta(days=1)
        today_bookings = self.bookings.filter(
            and_(Booking.rink_id == self.id,
                 Booking.start_date.between(start_of_today, end_of_today))
        ).all()
        return today_bookings

    def json(self) -> dict:
        return {
            "id": self.id,
            "name": str(self),
            "capacity": self.capacity,
            "status": self.current_status(),
            "max_groups": self.max_groups,
            "open": self.open,
            "close": self.close
        }

    def __str__(self) -> str:
        return self.name


class User(UserMixin, DB.Model):
    """
        A class used to store the user information
        Columns:
            id: the unique id
            email: the email associated with the user
            rink_id: the rink they are a coordinator or volunteer with
            is_administrator: whether the user is a town administrator
            is_coordinator: whether the user is a cooridinator for the rink
    """
    id = DB.Column(DB.Integer, primary_key=True)
    email = DB.Column(DB.String(256), unique=True)
    rink_id = DB.Column(DB.Integer, DB.ForeignKey('rink.id'))
    rink = DB.relationship(Rink)
    is_administrator = DB.Column(DB.Boolean)
    is_coordinator = DB.Column(DB.Boolean)

    def __init__(self, email: str, rink: Rink = None,
                 is_administrator: bool = False, is_coordinator: bool = False):
        self.email = email
        if rink is not None:
            self.rink_id = rink
        self.is_administrator = is_administrator
        self.is_coordinator

    def json(self) -> dict:
        return {
            "id": self.id,
            "rink": None if self.rink is None else self.rink.json(),
            "is_administrator": self.is_administrator,
            "is_coordinator": self.is_coordinator
        }

    def __str__(self):
        return self.email


class OAuth(OAuthConsumerMixin, DB.Model):
    provider_user_id = DB.Column(DB.String(256), unique=True, nullable=False)
    user_id = DB.Column(DB.Integer, DB.ForeignKey('user.id'), nullable=False)
    user = DB.relationship(User)


class Status(DB.Model):
    """
        A rink status update.
        Columns:
            id: the unique id
            open: whether the rink is open or not
            state: the state of the rink
            description: a short description about the rink status
            start_date: when the status is created
            end_date: when the status ends
            rink_id: the id of the rink that status is about
    """
    id = DB.Column(DB.Integer, primary_key=True)
    open = DB.Column(DB.Boolean)
    state = DB.Column(DB.String(256))
    description = DB.Column(DB.String(256))
    start_date = DB.Column(DB.DateTime)
    end_date = DB.Column(DB.DateTime)
    rink_id = DB.Column(DB.Integer, DB.ForeignKey('rink.id'))
    rink = DB.relationship(Rink)

    def __init__(self,
                 rink: Rink,
                 open: bool,
                 state: str,
                 description: str = None,
                 start_date: datetime = None,
                 end_date: datetime = None):
        if start_date is None:
            start_date = datetime.now()
        self.open = open
        self.state = state
        self.description = description
        self.start_date = start_date
        self.end_date = end_date
        self.rink_id = rink.id

    def __str__(self) -> str:
        """Returns a string representation of the status"""
        start_date = self.start_date.strftime("%Y-%m-%d %H:%M"),
        return f"{self.state} Last updated {start_date}"

    def json(self) -> dict:
        return {
            "id": self.id,
            "state": self.state,
            "open": self.open,
            "description": self.description,
            "start_date": self.start_date.strftime("%Y-%m-%d %H:%M"),
            "end_date": "" if self.end_date is None
                        else self.end_date.strftime("%Y-%m-%d %H:%M"),
            "rink": str(self.rink)
        }


class Booking(DB.Model):
    """
        A booking for a rink
        Columns:
            id: the unique id
            start_date: when the booking starts
            end_date: when the booking ends
            group_size: how big is the group
            rink_id: the id of the rink that is being booked
            user_id: who is making the booking
    """
    id = DB.Column(DB.Integer, primary_key=True)
    rink_id = DB.Column(DB.Integer, DB.ForeignKey('rink.id'))
    rink = DB.relationship(Rink)
    user_id = DB.Column(DB.Integer, DB.ForeignKey('user.id'))
    user = DB.relationship(User)
    start_date = DB.Column(DB.DateTime)
    end_date = DB.Column(DB.DateTime)
    group_size = DB.Column(DB.Integer)

    def __init__(self,
                 user: User,
                 rink: Rink,
                 start_date: datetime,
                 group_size: int = 1):
        self.rink_id = rink.id
        self.user_id = user.id
        self.start_date = start_date
        self.group_size = group_size
        self.end_date = start_date + timedelta(hours=1)

    def json(self) -> dict:
        return {
            "rink": self.rink.json(),
            "user": self.user.json(),
            "start_date": self.start_date.strftime("%Y-%m-%d %H:%M"),
            "group_size": self.group_size,
            "id": self.id
        }
