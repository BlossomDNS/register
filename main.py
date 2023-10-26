from flask import Flask, g, redirect, render_template, request,session, url_for
from admins import *
from github import *
from cloudflare import *
import subdomain_j

subdomain_j.setup()

app = Flask(__name__)
app.secret_key = 'somesecretkeythatonlyishouldknow'
cloudflare = Cloudflare(api_token=CLOUDFLARE_API_TOKEN,account_id=CLOUDFLARE_ACCOUNT_ID,zone_id=CLOUDFLARE_ZONE_ID)

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

    links = [{"title":pull["title"], "url": pull['html_url'], "date": datetime.strptime(pull['created_at'], "%Y-%m-%dT%H:%M:%SZ").strftime("%Y-%m-%d"), "user":pull["user"]["login"]} for pull in get_pr_date()]
    dns_content = [{"type":pull["type"], "name":pull["name"],"content":pull["content"],"proxied":pull["proxied"], "ttl":pull["ttl"]} for pull in cloudflare.getDNSrecords()]

    return render_template('admin.html', links = links, n = len(links), dns_content=dns_content, dns_n = len(dns_content), account_id=CLOUDFLARE_ACCOUNT_ID)

@app.route('/control', methods=['GET', 'POST']) #admin site soon
def control(output:str = "N/A"):
    if not g.user:
        return redirect(url_for('login'))
    
    if request.method == "POST":
        print(request.form)
        data = {}
        data["dns_record"] = request.form["dns_record"]
        data["type"] = request.form.get("type", None)
        data["dns_content"] = request.form.get("dns_content", None)

        
        if data["type"] == "A":
            return render_template("control.html", output=cloudflare.insert_A_record(DNS_RECORD_NAME=data["dns_record"], DNS_RECORD_CONTENT=data["dns_content"]).status_code)
        elif data["type"] == "CNAME":
            return render_template("control.html", output=cloudflare.insert_CNAME_record(DNS_RECORD_NAME=data["dns_record"], DNS_RECORD_CONTENT=data["dns_content"]).status_code)
        else:
            target_id = next((dns["id"] for dns in cloudflare.getDNSrecords() if dns["name"] == data["dns_record"]), None)
            
            if target_id == None:
                return render_template("control.html", output="Cannot find dns_record.")
            else:
                return render_template("control.html",output=cloudflare.delete(identifier=target_id).status_code)
    
    return render_template("control.html", output=output)
    
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