import requests
from flask import Flask, flash, g, redirect, render_template, request, session, url_for
from flask_github import GitHub
from admins import *
from github import *
from cloudflare import *
from routes.authentication import *
from data_sql import *
from discord import get_github_username, send_discord_message
from concurrency import *

database = dataSQL(dbfile="database.db")

app = Flask(__name__)
app.secret_key = "somesecretkeythatonlyishouldknow"
app.config["GITHUB_CLIENT_ID"] = CLIENT_ID
app.config["GITHUB_CLIENT_SECRET"] = CLIENT_SECRET
#GITHUB = GitHub(app)

CLOUDFLARE = {domain["url"]: Cloudflare(api_token=CLOUDFLARE_API_TOKEN, account_id=CLOUDFLARE_ACCOUNT_ID, zone_id=domain["cloudflare_zone_id"]) for domain in CLOUDFLARE_DOMAINS}


DOMAINS = set(CLOUDFLARE)

@app.after_request
def after_request_func(response):
    if session.get("id") != None:
        try:
            target = session.get("id")
            if request.path.count('/') == 1:
                send_discord_message(f"Session ``{target}`` as ``{get_github_username(github_id=target)}`` accessed the subdirectory ``{request.path}``")
        except:
            ...
        
    return response

@app.route("/")
def indexnormal():
    return render_template("home.html")

@app.route("/edit", methods=["GET","POST"])
def edit(error=""):
    if "id" not in session:
        return redirect("/")
    
    args = request.args.to_dict()
    INPUT = args["dom"]
    print(database.subdomains_from_token(session=session["id"]))
    if INPUT not in database.subdomains_from_token(session=session["id"]):
        return redirect("dashboard")
    
    DOMAIN = INPUT.split(".")[1]+"."+INPUT.split(".")[2]
    DOM = CLOUDFLARE[DOMAIN].find(INPUT)

    
    if ("dom" in args and args["dom"] is not None) == False:
        return redirect("dashboard")

    if request.method == "POST":
        print(request.form)
        NAME = request.form["name"]
        TYPE = request.form["type"]
        CONTENT = request.form["content"]

        id = CLOUDFLARE[DOMAIN].find(name=NAME)["id"]
        if CLOUDFLARE[DOMAIN].update(DNS_RECORD_NAME=str(NAME),DNS_RECORD_CONTENT=CONTENT,type=TYPE, id=id).status_code == 200:
            target = session["id"]
            send_discord_message(f"SESSION ID ``{target}`` as ``{get_github_username(github_id=target)}`` has **update** the domain: ``{INPUT}`` to following: ```TYPE   ->  {TYPE} \nNAME  ->  {NAME} \nCONTENT  ->  {CONTENT}```")
            return redirect("dashboard")
        else:
            return render_template("edit.html", domain=DOM, error="FAILED TO UPDATE ON CLOUDFLARE")

    
    
    return render_template("edit.html", domain=DOM, error=error)

@app.route("/claim", methods=["GET", "POST"])
def claim(error: str = ""):
    if "id" not in session:
        return redirect("/")
    target = session["id"]
    domains_thread = ThreadWithReturnValue(target=database.subdomains_from_token, args = (target,))
    domains_thread.start()
    max_domains_thread = ThreadWithReturnValue(target=dataSQL(dbfile="database.db").get_from_token, args=("max", target,))
    max_domains_thread.start()


    if request.method == "POST":
        INPUT = request.form["dns_submission"]
        DOMAIN = request.form["domain"]

        if len(INPUT.split(".")) > 1:
            return render_template("claim.html", error="Inappropriate Choice", domains=DOMAINS)

        if DOMAIN not in CLOUDFLARE:
            return render_template("claim.html", error="We Don't Offer That Domain", domains=DOMAINS)

        for x in CLOUDFLARE[DOMAIN].getDNSrecords():
            if INPUT == x["name"]:
                return render_template("claim.html", error="Domain already taken", domains=DOMAINS)

        max_domains = max_domains_thread.join()
        domains = domains_thread.join()
        if max_domains <= len(domains):
            return render_template("claim.html", error="You already have the maximum number of domains.")

        
        subdomain = f"{INPUT}.{DOMAIN}"

        # Give the user the subdomain
        response = CLOUDFLARE[DOMAIN].insert_CNAME_record(
            DNS_RECORD_NAME=subdomain,
            DNS_RECORD_CONTENT="github.com",
            comment=f"OWNER RESPONSIBLE IS {target} as {get_github_username(github_id=target)}"
        )

        if response.status_code != 200:
            Thread(target=send_discord_message, args = (response.text,)).start()
            return render_template("claim.html", error="Failed to POST to Cloudflare", domains=DOMAINS)

        database.new_subdomain(token=session["id"], subdomain=subdomain)

        Thread(target=send_discord_message, args = (f"SESSION ID ``{target}`` as ``{get_github_username(github_id=target)}`` has **claimed** the domain: ``{subdomain}``",)).start()

        return redirect("dashboard")


    else:
        return render_template("claim.html", error=error, domains=DOMAINS)


@app.before_request
def before_request():
    g.user = None
    if "user_id" in session:
        user = [x for x in ADMIN_ACCTS if x.id == session["user_id"]][0]
        g.user = user
    



@app.route("/admin", methods=["GET", "POST"])  # admin site soon
def admin():
    if not g.user:
        return redirect(url_for("adminlogin"))
    subdomains = []

    for domain in CLOUDFLARE_DOMAINS:
        yes = CLOUDFLARE[domain["url"]].getDNSrecords()
        for ye in yes:
            subdomains.append(
                {
                    "name": ye["name"],
                    "type": ye["type"],
                    "content": ye["content"],
                    "id": ye["id"],
                    "proxied": ye["proxied"],
                }
            )
    
    args = request.args.to_dict()
    if "delete" in args and args["delete"] is not None:

        INPUT = args["delete"]
        print(INPUT)
        insert = INPUT.split(".")
        DOMAIN = insert[1] + "." + insert[2]

        if CLOUDFLARE[DOMAIN].find_and_delete(INPUT):
            database.delete(subdomain=INPUT)
        
        target = session["admin_email"]
        send_discord_message(f":safety_vest: ADMIN ``{target}`` has deleted the domain ``{INPUT}``. :safety_vest: ")
        
        return redirect("admin")


    return render_template(
        "admin.html", subdomains=subdomains, account_id=CLOUDFLARE_ACCOUNT_ID
    )


@app.route("/dashboard", methods=["GET", "POST"])
def dashboard(response: str = ""):
    if "id" not in session:
        return redirect("login")
    domains_thread = ThreadWithReturnValue(target=database.subdomains_from_token, args=(session["id"],))
    domains_thread.start()
    all_sub_domains_thread = ThreadWithReturnValue(target=cloudf_doms, args=(CLOUDFLARE_DOMAINS, CLOUDFLARE))
    all_sub_domains_thread.start()
    target = session["id"]
    
    user_info_thread = ThreadWithReturnValue(target=requests.get,
        kwargs={'url': f"https://api.github.com/user/{target}", "headers": {'Authorization': 'token ' + GITHUB_TOKEN}}
        
        
    )
    user_info_thread.start()
    
    args = request.args.to_dict()
    if "delete" in args and args["delete"] is not None:

        INPUT = args["delete"]
        insert = INPUT.split(".")
        if len(insert) != 3: #subdomain | domain | com (3)
            return redirect("dashboard")
        DOMAIN = insert[1] + "." + insert[2]


        domains = domains_thread.join()
        if (INPUT in domains) == False: #if user doesn't own domain, return them back
            return redirect("dashboard")


        if CLOUDFLARE[DOMAIN].find_and_delete(INPUT):
            database.delete(subdomain=INPUT)
            target = session["id"]
            send_discord_message(f"SESSION ID ``{target}`` as ``{get_github_username(github_id=target)}`` has **deleted** the domain: ``{INPUT}``.")

        return redirect("dashboard")




    user_info = user_info_thread.join().json()
    user_profile_picture = user_info["avatar_url"]
    user_company = user_info["company"]

    
    domains = domains_thread.join()
    if domains == []:
        return render_template(
            "dashboard.html",
            subdomains=[],
            github_username=request.cookies.get("username"),
            github_profile=user_profile_picture,
            github_company=user_company,
            response=response
        )
    
    all_sub_domains = all_sub_domains_thread.join()

    user_subdomains = [
        possible_domain
        for possible_domain in all_sub_domains
        if possible_domain["name"] in domains
    ]

    return render_template(
        "dashboard.html",
        subdomains=user_subdomains,
        github_username=request.cookies.get("username"),
        github_profile=user_profile_picture,
        github_company=user_company,
        response=response
    )


#@app.route("/control", methods=["GET", "POST"])  # admin site soon
#def control(output: str = "N/A"):
#    if not g.user:
#        return redirect(url_for("login"))
#
#    if request.method == "POST":
#        data = {}
#        data["dns_record"] = request.form["dns_record"]
#        data["type"] = request.form.get("type")
#        data["url"] = request.form.get("url")
#        data["dns_content"] = request.form.get("dns_content")
#        if data["type"].lower() == "a":
#            CLOUDFLARE[data["url"]].insert_A_record(
#                data["dns_record"], data["dns_content"], PROXIED=False
#            )
#        elif data["type"].lower() == "cname":
#            CLOUDFLARE[data["url"]].insert_CNAME_record(
#                data["dns_record"], data["dns_content"], PROXIED=False
#            )
#        else:
#            return "wrong type"
#
#    return render_template("control.html", output=output, urls=CLOUDFLARE_DOMAINS)


@app.route("/loginadmin", methods=["GET", "POST"])
def loginadmin():
    if request.method == "POST":
        session.pop("user_id", None)

        try:
            email = request.form["email"]
            pw = request.form["password"]

            user = [x for x in ADMIN_ACCTS if x.username == email][0]
            if user and user.password == pw:
                session["user_id"] = user.id
                session["admin_email"] = user.username
                send_discord_message(f":safety_vest: ADMIN ``{user.username}`` has logged in. :safety_vest: ")
                return redirect(url_for("admin"))
            
            send_discord_message(f":octagonal_sign: ADMIN ``{user.username}`` has failed login attempt. :octagonal_sign: ")
            return redirect(url_for("loginadmin"))
        except Exception as e:
            send_discord_message(f":octagonal_sign:  __Attempted Login Failed...__ Error: ```{e}``` :octagonal_sign: ")
        
    return render_template("login.html")


if __name__ == "__main__":
    # from waitress import serve
    # serve(app, host="0.0.0.0", port=8080)
    app.register_blueprint(authentication)
    app.run(host="0.0.0.0", port=PORT, debug=False, threaded=True)
