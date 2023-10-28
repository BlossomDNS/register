from flask import Flask, g, redirect, render_template, request,session, url_for
from admins import *
from github import *
from cloudflare import *


app = Flask(__name__)
app.secret_key = 'somesecretkeythatonlyishouldknow'

cloudflare = {}
for domain in CLOUDFLARE_DOMAINS:
    cloudflare[domain['url']] = Cloudflare(api_token=CLOUDFLARE_API_TOKEN,account_id=CLOUDFLARE_ACCOUNT_ID,zone_id=domain['cloudflare_zone_id'])

#load_github_sites(app=app) #loads sites from github api


@app.route('/')
def index():
    return render_template('home.html')


# ADMIN WEBSITE CODE
@app.before_request
def before_request():
    g.user = None
    

    if 'user_id' in session:
        user = [x for x in ADMIN_ACCTS if x.id == session['user_id']][0]
        g.user = user


@app.route('/admin', methods=['GET', 'POST']) #admin site soon
def admin():
    if not g.user:
        return redirect(url_for('login'))
    subdomains = []

    for domain in CLOUDFLARE_DOMAINS:
        yes = cloudflare[domain['url']].getDNSrecords()
        for ye in yes:
            subdomains.append({"name": ye['name'], "type": ye['type'], "content": ye['content'], "id": ye['id'], "proxied": ye['proxied']})
    return render_template('admin.html', subdomains=subdomains, account_id=CLOUDFLARE_ACCOUNT_ID)

@app.route('/control', methods=['GET', 'POST']) #admin site soon
def control(output:str = "N/A"):
    if not g.user:
        return redirect(url_for('login'))
    
    if request.method == "POST":
        data = {}
        data["dns_record"] = request.form["dns_record"]
        data["type"] = request.form.get("type")
        data["url"] = request.form.get("url")
        data["dns_content"] = request.form.get("dns_content")
        if data['type'].lower() == "a":
            cloudflare[data['url']].insert_A_record(data["dns_record"], data["dns_content"], PROXIED=False)
        elif data['type'].lower() == "cname":
            cloudflare[data['url']].insert_CNAME_record(data["dns_record"], data["dns_content"], PROXIED=False)    
        else:
            return "wrong type"
        
        
        
    
    return render_template("control.html", output=output, urls=CLOUDFLARE_DOMAINS)
    
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        session.pop('user_id', None)
        
        email = request.form["email"]
        pw = request.form["password"]

        user = [x for x in ADMIN_ACCTS if x.username == email][0]
        if user and user.password == pw:
            session['user_id'] = user.id
            return redirect(url_for('admin'))
        
        return redirect(url_for('login'))
        
    return render_template("login.html")

if __name__ == '__main__':
    #from waitress import serve
    #serve(app, host="0.0.0.0", port=8080)
    app.run(host='0.0.0.0')


