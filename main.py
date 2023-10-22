import cloudflare
from flask import Flask, g, redirect, render_template, request,session, url_for
from admins import *
from github import *


app = Flask(__name__)
app.secret_key = 'somesecretkeythatonlyishouldknow'

load_github_sites(app=app)

@app.before_request
def before_request():
    g.user = None

    if 'user_id' in session:
        user = [x for x in admin_accts if x.id == session['user_id']][0]
        g.user = user


@app.route('/profile')
def profile():
    if not g.user:
        return redirect(url_for('login'))

    return render_template('test.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        session.pop('user_id', None)
        
        email = request.form["username"]
        pw = request.form["password"]

        user = [x for x in admin_accts if x.username == email][0]
        if user and user.password == pw:
            session['user_id'] = user.id
            return redirect(url_for('test'))
        
        return redirect(url_for('login'))
        
    return render_template("login.html")


if __name__ == '__main__':
    app.run()