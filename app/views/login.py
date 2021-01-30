from flask import render_template, redirect, url_for, current_app
from flask_login import current_user, logout_user, login_required
from app.authentication import is_facebook_supported, is_github_supported,\
    is_gmail_supported
from app.logging import LOGGER


@current_app.route("/login")
def loginpage():
    """A route to login the user."""
    return render_template("login.html",
                           github_enabled=is_github_supported(),
                           facebook_enabled=is_facebook_supported(),
                           gmail_enabled=is_gmail_supported())


@current_app.route("/logout")
@login_required
def logout():
    """A route to log out the user."""
    LOGGER.info(f"{current_user} has logged out")
    logout_user()
    return redirect(url_for("homepage"))
