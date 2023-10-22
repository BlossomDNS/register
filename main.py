import cloudflare
from flask import Flask, g, redirect, render_template, request,session, url_for
import admins

app = Flask(__name__)



@app.route('/test')
def profile():
    if not g.user:
        return redirect(url_for('test'))

    return render_template('profile.html')

@app.route('/login',method = ["GET","POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        pw = request.form["password"]

        if (email in admins.emails) and (pw in admins.passwords):
             
        
    return render_template("login.html")

if __name__ == '__main__':
    app.run()