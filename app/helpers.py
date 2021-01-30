# -*- coding: utf-8 -*-
"""Holds some helper functions and methods."""
from dateutil import tz
from datetime import datetime
from flask import current_app
from json import loads as loader


def loads(data):
    """Loads the json data"""
    try:
        data = loader(data)
    except Exception:
        data = loader(data.decode('utf-8'))
    return data


def get_time_today(hour: int, minute: int = 0) -> datetime:
    """Returns a time that is today in the app timezone."""
    today = datetime.utcnow().date()
    return datetime(today.year, today.month, today.day,
                    hour=hour, minute=minute,
                    tzinfo=tz.gettz(current_app.config["TIMEZONE"]))
