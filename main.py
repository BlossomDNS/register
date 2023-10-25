from flask import Flask, g, redirect, render_template, request,session, url_for
from admins import *
from github import *
from cloudflare import *

app = Flask(__name__)
app.secret_key = 'somesecretkeythatonlyishouldknow'

load_github_sites(app=app) #loads sites from github api

@app.before_request
def before_request():
    g.user = None

    if 'user_id' in session:
        user = [x for x in admin_accts if x.id == session['user_id']][0]
        g.user = user


@app.route('/admin', methods=['GET', 'POST']) #admin site soon
def admin():
    if not g.user:
        return redirect(url_for('login'))
    
    date_format = "%Y-%m-%dT%H:%M:%SZ"
    pulls_data = get_pr_date()
    links = [{"title":pull["title"], "url": pull['html_url'], "date": datetime.strptime(pull['created_at'], date_format).strftime("%Y-%m-%d")} for pull in pulls_data]

    return render_template('admin.html', links = links, n = len(links))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        session.pop('user_id', None)
        
        email = request.form["email"]
        pw = request.form["password"]

        user = [x for x in admin_accts if x.username == email][0]
        if user and user.password == pw:
            session['user_id'] = user.id
            return redirect(url_for('admin'))
        
        return redirect(url_for('login'))
        
    return render_template("login.html")

if __name__ == '__main__':
    app.run(host='0.0.0.0')