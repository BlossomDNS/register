from flask import Blueprint, current_app, url_for, session, redirect, make_response
from authlib.integrations.flask_client import OAuth
from authlib.common.errors import AuthlibBaseError
from config import *
import sqlite3
from main import database
from discord import *

authentication = Blueprint("authentication", __name__)
oauth = OAuth(current_app)
GITHUB = oauth.register(
    name="github",
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    access_token_url="https://github.com/login/oauth/access_token",
    access_token_params=None,
    authorize_url="https://github.com/login/oauth/authorize",
    authorize_params=None,
    api_base_url="https://api.github.com/",
    client_kwargs={"scope": "public_repo"},
)


@authentication.route("/login")
def login():
    return GITHUB.authorize_redirect(GIT_OAUTH_CALLBACK_URL)


@authentication.route("/authorize")
def authorize():
    resp = oauth.create_client("github").get(
        "user", token=GITHUB.authorize_access_token()
    )
    profile = resp.json()

    x = database.use_database(
        "SELECT COUNT(*) FROM users WHERE token = ?", (profile["id"],)
    )
    if int(x[0]) >= 1:  # check if acct with token already exists
        session["id"] = profile["id"]
        res = make_response(redirect(url_for("dashboard")))
        res.set_cookie("id", str(profile["id"]))
        res.set_cookie("username", str(profile["login"]))
        target = session["id"]
        send_discord_message(f"ACCT LOGGED WITH SESSION ID ``{target}`` as ``{get_github_username(github_id=target)}``")
        return res

    database.use_database(
        "INSERT INTO users (username, token) VALUES (?, ?)",
        (
            profile["login"],
            profile["id"],
        ),
    )
    print(profile)
    session["id"] = profile["id"]
    print(session["id"])
    res = make_response(redirect(url_for("dashboard")))
    res.set_cookie("id", str(profile["id"]))
    res.set_cookie("username", str(profile["login"]))
    target = session["id"]
    send_discord_message(f":green_heart: :green_heart: :green_heart: NEW ACCT CREATED! SESSION ID ``{target}`` as ``{get_github_username(github_id=target)}``")
    return res
