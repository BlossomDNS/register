from flask import Blueprint, current_app, url_for, session, redirect, make_response
from authlib.integrations.flask_client import OAuth
from authlib.common.errors import AuthlibBaseError
from config import *
import sqlite3

def use_database(query: str, values:tuple=None):
    
    connection = sqlite3.connect("database.db")
    connection.execute(query, values)
    connection.commit()
    connection.close()


authentication = Blueprint('authentication', __name__)
oauth = OAuth(current_app)
github = oauth.register(
    name='github',
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    access_token_url='https://github.com/login/oauth/access_token',
    access_token_params=None,
    authorize_url='https://github.com/login/oauth/authorize',
    authorize_params=None,
    api_base_url='https://api.github.com/',
    client_kwargs={'scope': 'public_repo'},
)


@authentication.route('/login')
def login():
    github = oauth.create_client('github')
    redirect_uri = url_for('authentication.authorize', _external=True)
    return github.authorize_redirect(redirect_uri)


@authentication.route('/authorize')
def authorize():
    github = oauth.create_client('github')
    token = github.authorize_access_token()
    resp = github.get('user', token=token)
    profile = resp.json()
    use_database("INSERT INTO users (username, token) VALUES (?, ?)", (profile['login'], profile['id'],))
    print(profile)
    session['id'] = profile['id']
    print(session['id'])
    res = make_response(redirect(url_for("dashboard")))
    res.set_cookie("id", str(profile['id']))
    res.set_cookie("username", str(profile['login']))
    return res