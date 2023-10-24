from flask import Flask, g, redirect, render_template, request,session, url_for
from admins import *
from github import *
from cloudflare import *
import subdomain_j

subdomain_j.setup()

app = Flask(__name__)
app.secret_key = 'somesecretkeythatonlyishouldknow'
cloudflare = Cloudflare(api_token=cloudflare_api_token,account_id=cloudflare_account_id,zone_id=cloudflare_zone_id)

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

    links = [{"title":pull["title"], "url": pull['html_url'], "date": datetime.strptime(pull['created_at'], "%Y-%m-%dT%H:%M:%SZ").strftime("%Y-%m-%d")} for pull in get_pr_date()]
    dns_content = [{"type":pull["type"], "name":pull["name"],"content":pull["content"],"proxied":pull["proxied"], "ttl":pull["ttl"]} for pull in cloudflare.getDNSrecords()]

    return render_template('admin.html', links = links, n = len(links), dns_content=dns_content, dns_n = len(dns_content), account_id=cloudflare_account_id)

@app.route('/control', methods=['GET', 'POST']) #admin site soon
def control():
    if not g.user:
        return redirect(url_for('login'))
    
    if request.method == "POST":
        print(request.form)
        data = {}
        data["dns_record"] = request.form["dns_record"]

        try:
            data["type"] = request.form["type"]
        except:
            data["type"] = None

        try:
            data["dns_content"] = request.form["dns_content"]
        except:
            data["dns_content"] = None

        
        if data["type"] == "A":
            cloudflare.insert_A_record(DNS_RECORD_NAME=data["dns_record"], DNS_RECORD_CONTENT=data["dns_content"])
        elif data["type"] == "CNAME":
            cloudflare.insert_CNAME_record(DNS_RECORD_NAME=data["dns_record"], DNS_RECORD_CONTENT=data["dns_content"])
        else:
            target_id = 0

            for dns in cloudflare.getDNSrecords():
                if dns["name"] == data["dns_record"]:
                    target_id = dns["id"]
            
            cloudflare.delete(identifier=target_id)
    
    return render_template("control.html")
    
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
    app.run()