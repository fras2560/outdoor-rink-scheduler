# -*- coding: utf-8 -*-
"""Holds all website the views."""
__all__ = []
from flask import send_from_directory, current_app
import pkgutil
import inspect


@current_app.route("/robots.txt")
def robot():
    """A route for the google web crawler."""
    return send_from_directory(current_app.static_folder, "robots.txt")


for loader, name, is_pkg in pkgutil.walk_packages(__path__):
    module = loader.find_module(name).load_module(name)

    for name, value in inspect.getmembers(module):
        if name.startswith('__'):
            continue

        globals()[name] = value
        __all__.append(name)
