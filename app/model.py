# -*- coding: utf-8 -*-
"""Holds a database model for the application."""
from app.logging import LOGGER
from app.helpers import get_time_today, localize_date
from flask_sqlalchemy import SQLAlchemy
from flask_dance.consumer.storage.sqla import OAuthConsumerMixin
from flask_login import UserMixin
from sqlalchemy import and_
from typing import TypedDict
from datetime import datetime, timedelta


"""The database object."""
DB = SQLAlchemy()


def have_booked_already(bookings: list, start: datetime,
                        end: datetime = None) -> bool:
    """Returns whether have already booked for given hour"""
    for booking in bookings:
        if (end is None and booking.get_start() <= start and
                booking.get_end() >= start):
            return True
        elif (end is not None and booking.get_start() <= end and
              booking.get_end() >= start):
            return True
    return False


class Timeslot(TypedDict):
    """Information about a timeslot for a given rink."""
    start: datetime
    end: datetime
    display: str
    booked: bool
    number: int
    capacity: int
    user_booked: bool

    @staticmethod
    def empty_timeslot(start: datetime, end: datetime,
                       capacity: int) -> 'Timeslot':
        """Returns an empty rink timeslot."""
        return {
            "start": start,
            "end": end,
            "hour": int(start.strftime("%H")),
            "display": start.strftime("%H:%M") + " - " + end.strftime("%H:%M"),
            "booked": False,
            "number": 0,
            "capacity": capacity,
            "user_booked": False
        }

    @staticmethod
    def add_booking(timeslot) -> None:
        """Add a booking to the given timeslot."""
        timeslot["number"] += 1
        if timeslot["number"] >= timeslot["capacity"]:
            timeslot["booked"] = True


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
            map_link: a link to the google map of the rink
    """
    id = DB.Column(DB.Integer, primary_key=True)
    name = DB.Column(DB.String(256))
    statuses = DB.relationship('Status',
                               backref='statuses', lazy='dynamic')
    bookings = DB.relationship('Booking',
                               backref='bookings', lazy='dynamic')
    coordinators = DB.relationship('People',
                                   backref='coordinators', lazy='dynamic')
    capacity = DB.Column(DB.Integer)
    max_groups = DB.Column(DB.Integer)
    open = DB.Column(DB.Integer)
    close = DB.Column(DB.Integer)
    map_link = DB.Column(DB.Text())

    def __init__(self,
                 name: str,
                 capacity: int = 25,
                 max_groups: int = 25,
                 open: int = 8,
                 close: int = 22,
                 link: str = None):
        assert close >= open
        self.name = name
        self.capacity = capacity
        self.max_groups = max_groups
        self.open = open
        self.close = close
        self.map_link = link

    def get_capacity(self) -> int:
        return self.capacity

    def current_status(self) -> 'Status':
        """Returns the current status of the rink"""
        for status in self.statuses:
            if status.end_date is None:
                return status
        return None

    def timeslots(self, hour: int = -1) -> list:
        """Returns list of timeslots todays

        If given a hour then timeslot is specific to the hour given.

        Args:
            hour (int, optional): the hour of the timeslot.
                Default all timeslots
        Returns:
            list: a list of timeslots
        """
        timeslots = []
        if hour == -1:
            for time in range(self.open, self.close):
                start = get_time_today(time)
                end = get_time_today(time, minute=59)
                timeslot = Timeslot.empty_timeslot(start, end, self.capacity)
                for booking in self.today_bookings(time):
                    Timeslot.add_booking(timeslot)
                timeslots.append(timeslot)
            return timeslots
        else:
            start = get_time_today(hour)
            end = get_time_today(hour, minute=59)
            timeslot = Timeslot.empty_timeslot(start, end, self.capacity)
            for booking in self.today_bookings(hour):
                Timeslot.add_booking(timeslot)
            return [timeslot]

    def today_bookings(self, hour: int = -1) -> list:
        """Returns the booking for the rink today"""
        if hour == -1:
            start_of_today = get_time_today(0)
            end_of_today = get_time_today(23, minute=59)
        else:
            start_of_today = get_time_today(hour)
            end_of_today = get_time_today(hour, minute=59)
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
            "close": self.close,
            "map_link": self.map_link
        }

    def __str__(self) -> str:
        return self.name


class People(UserMixin, DB.Model):
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
            self.rink = rink
        self.is_administrator = is_administrator
        self.is_coordinator = is_coordinator

    def json(self) -> dict:
        return {
            "id": self.id,
            "rink": None if self.rink is None else self.rink.json(),
            "is_administrator": self.is_administrator,
            "is_coordinator": self.is_coordinator,
            "email": self.email
        }

    def __str__(self):
        return self.email

    def bookings(self, rink=None):
        """Return bookings for the person if given rink then filter by rink"""
        start_of_today = get_time_today(0)
        end_of_today = get_time_today(23, minute=59)
        query = Booking.query.filter(Booking.user_id == self.id).filter(
            Booking.start_date.between(start_of_today, end_of_today))
        if rink is not None:
            query.filter(Booking.rink_id == rink.id)
        return query.all()


class OAuth(OAuthConsumerMixin, DB.Model):
    """Authentication for some provider that maps to some user"""
    provider_user_id = DB.Column(DB.String(256), unique=True, nullable=False)
    user_id = DB.Column(DB.Integer, DB.ForeignKey('people.id'), nullable=False)
    user = DB.relationship(People)


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
        self.rink = rink

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
    user_id = DB.Column(DB.Integer, DB.ForeignKey('people.id'))
    user = DB.relationship(People)
    start_date = DB.Column(DB.DateTime)
    end_date = DB.Column(DB.DateTime)
    group_size = DB.Column(DB.Integer)

    def __init__(self,
                 user: People,
                 rink: Rink,
                 start_date: datetime,
                 group_size: int = 1):
        self.rink = rink
        self.user = user
        self.start_date = start_date
        self.group_size = group_size
        self.end_date = start_date + timedelta(minutes=59)

    def get_start(self) -> datetime:
        """Returns the start date of the booking"""
        return localize_date(self.start_date)

    def get_end(self) -> datetime:
        """Returns the end date of the booking"""
        return localize_date(self.end_date)

    def json(self) -> dict:
        return {
            "rink": self.rink.json(),
            "user": self.user.json(),
            "start_date": self.start_date.strftime("%Y-%m-%d %H:%M"),
            "end_date": self.end_date.strftime("%Y-%m-%d %H:%M"),
            "group_size": self.group_size,
            "id": self.id,
            'time': self.start_date.strftime("%H:%M"),
            'hour': int(self.start_date.strftime("%H"))
        }
