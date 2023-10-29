from flask import Flask, flash, g, redirect, render_template, request,session, url_for
from flask_github import GitHub
from admins import *
from github import *
from cloudflare import *
import sqlite3
from routes.authentication import * 
from data_sql import *

database = dataSQL(dbfile="database.db")

app = Flask(__name__)
app.secret_key = 'somesecretkeythatonlyishouldknow'
app.config['GITHUB_CLIENT_ID'] = CLIENT_ID
app.config['GITHUB_CLIENT_SECRET'] = CLIENT_SECRET
github = GitHub(app)

cloudflare = {}
for domain in CLOUDFLARE_DOMAINS:
    cloudflare[domain['url']] = Cloudflare(api_token=CLOUDFLARE_API_TOKEN,account_id=CLOUDFLARE_ACCOUNT_ID,zone_id=domain['cloudflare_zone_id'])


@app.route('/')
def indexnormal(): return render_template('home.html')

@app.route('/delete', methods=['GET','POST'])
def delete(error: str = ""):
    if request.method == "POST":

        INPUT = request.form["dns_submission"]
        insert = INPUT.split(".")
        DOMAIN = insert[1]+"."+insert[2]


        #Check if domain is taken or not / free and availiable
        if (DOMAIN in list(cloudflare)) != True:
            return render_template("claim.html", error="We Don't Offer That Domain")
        
        domains = database.subdomains_from_token(session=session["id"])

        print(cloudflare[DOMAIN].getDNSrecords())

        if (INPUT in domains) == False:
            return render_template("delete.html",error="You don't own that domain")
        
        for sub in cloudflare[DOMAIN].getDNSrecords():
            if sub == INPUT:
                if cloudflare[DOMAIN].delete(sub["id"]) != 200:
                    return render_template("delete.html", error="Failed to POST to Cloudflare")
            
            else:
                return render_template("delete.html", error="Domain is not used")
        
        if INPUT in domains:
            domains.remove(INPUT)

        database.use_database("UPDATE users SET subdomains = ? WHERE token = ?", (f"""{str(domains).strip()}""", session['id'],))
        
        return render_template("delete.html", error="SUCCESS")
    
    else:
        return render_template("delete.html", error=error)

@app.route('/claim', methods=['GET', 'POST'])
def claim(error: str = ""):
    if request.method == "POST":

        INPUT = request.form["dns_submission"]
        insert = INPUT.split(".")
        DOMAIN = insert[1]+"."+insert[2]

        if len(insert) != 3:
            return render_template("claim.html", error="Bad Insert")


        #Check if domain is taken or not / free and availiable
        if (DOMAIN in list(cloudflare)) != True:
            return render_template("claim.html", error="We Don't Offer That Domain")
        
        for x in cloudflare[DOMAIN].getDNSrecords():
            if INPUT == x["name"]:
                return render_template("claim.html", error="Domain already taken")
        
        if cloudflare[DOMAIN].insert_CNAME_record(DNS_RECORD_NAME=INPUT, DNS_RECORD_CONTENT="github.com").status_code != 200:    
            return render_template("claim.html", error="Failed to POST to Cloudflare")
        

        domains = database.subdomains_from_token(session=session["id"])
        if database.get_from_token(need="max",session=session["id"]) <= len(domains):
            return render_template("claim.html", error="You already have a max # of domans.")
        domains.append(INPUT)
        database.use_database("UPDATE users SET subdomains = ? WHERE token = ?", (f"""{str(domains).strip()}""", session['id'],))
        
        
        return render_template("claim.html", error="SUCCESS")
    
    else:
        return render_template("claim.html", error=error)

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

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if request.method == "POST":
        data = {}
        data["dns_record"] = request.form["dns_record"]
        data["type"] = request.form.get("type")
        data["url"] = request.form.get("url")
        data["dns_content"] = request.form.get("dns_content")
        subdomains = database.use_database("SELECT subdomains FROM users where token = ?", (session['id'],))
        if data['type'].lower() == "a":
            
            database.use_database("UPDATE users SET subdomains = ? WHERE token = ? '", (f"{subdomains}<>{data['dns_record']}.{data['url']}", session['id'],))
            cloudflare[data['url']].insert_A_record(data["dns_record"], data["dns_content"], PROXIED=False)
        elif data['type'].lower() == "cname":
            database.use_database("UPDATE users SET subdomains = ? WHERE token = ? '", (f"{subdomains}<>{data['dns_record']}.{data['url']}", session['id'],))
            
            cloudflare[data['url']].insert_CNAME_record(data["dns_record"], data["dns_content"], PROXIED=False)    
        else:
            return "wrong type"
    
    all_sub_domains=[]
    for all_domain in CLOUDFLARE_DOMAINS:
        records = cloudflare[all_domain['url']].getDNSrecords()
        for record in records:
            all_sub_domains.append({"name": record['name'], "type": record['type'], "content": record['content'], "id": record['id'], "proxied": record['proxied']})
    
    
    domains = database.subdomains_from_token(session=session["id"])

    if domains == []:
        return render_template('dashboard.html', subdomains=[], account_id=CLOUDFLARE_ACCOUNT_ID, github_username=request.cookies.get("username"))


    user_subdomains = [possible_domain for possible_domain in all_sub_domains if possible_domain['name'] in domains]    

    print(user_subdomains)
    
    return render_template('dashboard.html', subdomains=user_subdomains, account_id=CLOUDFLARE_ACCOUNT_ID, github_username=request.cookies.get("username"))

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
    
@app.route('/loginadmin', methods=['GET', 'POST'])
def loginadmin():
    if request.method == "POST":
        session.pop('user_id', None)
        
        email = request.form["email"]
        pw = request.form["password"]

        user = [x for x in ADMIN_ACCTS if x.username == email][0]
        if user and user.password == pw:
            session['user_id'] = user.id
            return redirect(url_for('admin'))
        
        return redirect(url_for('loginadmin'))
        
    return render_template("login.html")

if __name__ == '__main__':
    #from waitress import serve
    #serve(app, host="0.0.0.0", port=8080)
    app.register_blueprint(authentication)
    app.run(host='0.0.0.0')


