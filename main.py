import requests
from flask import Flask, g, redirect, render_template, request, session, url_for
from admins import *
from cloudflare import *
from routes.authentication import *
from data_sql import *
from discord import get_github_username, send_discord_message
from concurrency import *
from threadedreturn import ThreadWithReturnValue


def define_app(database = dataSQL(dbfile="database.db")):
    """
    This defines the application of the web app
    database doesn't need to be defined (as it is already pre-defined)
    returns the application
    """
    #Flask App
    app = Flask(__name__)
    app.secret_key = SECRET_KEY
    app.config["GITHUB_CLIENT_ID"] = CLIENT_ID
    app.config["GITHUB_CLIENT_SECRET"] = CLIENT_SECRET
    #Cloudflare global variables are in cloudflare.py since a lot of .py files uses them


    #USER SIDE
    #===============================
    #/
    @app.route("/")
    def indexnormal():
        return render_template("home.html")

    #/edit
    @app.route("/edit", methods=["GET","POST"])
    def edit():
        if "id" not in session:
            return redirect("/")
        
        args = request.args.to_dict()
        INPUT = args["dom"]
        if INPUT not in database.subdomains_from_token(session=session["id"]):
            return redirect("dashboard")
        
        DOMAIN = INPUT.split(".")[1]+"."+INPUT.split(".")[2]
        DOM = CLOUDFLARE[DOMAIN].find(INPUT)

        
        if ("dom" in args and args["dom"] is not None) == False:
            return redirect("dashboard")

        if request.method == "POST":
            NAME = request.form["name"]
            TYPE = request.form["type"]
            CONTENT = request.form["content"]
            CLOUDFLARE = CLOUDFLARE()

            id = CLOUDFLARE[DOMAIN].find(name=NAME)["id"]
            if CLOUDFLARE[DOMAIN].update(DNS_RECORD_NAME=str(NAME),DNS_RECORD_CONTENT=CONTENT,type=TYPE, id=id).status_code == 200:
                target = session["id"]
                send_discord_message(f"SESSION ID ``{target}`` as ``{get_github_username(github_id=target)}`` has **update** the domain: ``{INPUT}`` to following: ```TYPE   ->  {TYPE} \nNAME  ->  {NAME} \nCONTENT  ->  {CONTENT}```")
                return redirect("dashboard")
            else:
                return render_template("edit.html", domain=DOM, error="FAILED TO UPDATE ON CLOUDFLARE")

        
        
        return render_template("edit.html", domain=DOM, error="")

    #/claim
    @app.route("/claim", methods=["GET", "POST"])
    def claim():
        if "id" not in session:
            return redirect("/")
        target = session["id"]

        if request.method == "POST":
            
            domains_thread = ThreadWithReturnValue(target=database.subdomains_from_token, args = (target,))
            domains_thread.start()
            max_domains_thread = ThreadWithReturnValue(target=dataSQL(dbfile="database.db").get_from_token, args=("max", target,))
            max_domains_thread.start()

            INPUT = request.form["dns_submission"]
            DOMAIN = request.form["domain"]

            if len(INPUT.split(".")) > 1:
                return render_template("claim.html", error="Inappropriate Choice", domains=DOMAINS())

            CF = CLOUDFLARE()
            if DOMAIN not in CF:
                return render_template("claim.html", error="We Don't Offer That Domain", domains=DOMAINS())
            
            SUBDOMAIN = f"{INPUT}.{DOMAIN}"

            if CF[DOMAIN].find(name=SUBDOMAIN):
                return render_template("claim.html", error="Domain already taken", domains=DOMAINS())

            max_domains = max_domains_thread.join()
            if max_domains <= len(domains_thread.join()):
                return render_template("claim.html", error="You already have the maximum number of domains.",domains=DOMAINS())


            # Give the user the subdomain
            response = CF[DOMAIN].insert_CNAME_record(
                DNS_RECORD_NAME=SUBDOMAIN,
                DNS_RECORD_CONTENT="github.com",
                comment=f"OWNER RESPONSIBLE IS {target} as {get_github_username(github_id=target)}"
            )

            if response.status_code != 200:
                Thread(target=send_discord_message, args = (response.text,)).start()
                return render_template("claim.html", error="Domain already exist on Cloudflare.", domains=DOMAINS())

            database.new_subdomain(token=session["id"], subdomain=SUBDOMAIN)
            t = ThreadWithReturnValue(target=CACHE_INSTANCE().get_subdomains, args=(True,))
            t.start()
            Thread(target=send_discord_message, args = (f"SESSION ID ``{target}`` as ``{get_github_username(github_id=target)}`` has **claimed** the domain: ``{SUBDOMAIN}``",)).start()
            t.join()
            
            return redirect("dashboard") #successful process


        else:
            return render_template("claim.html", error="", domains=DOMAINS())

    #/dashboard
    @app.route("/dashboard", methods=["GET", "POST"])
    def dashboard(response: str = ""):
        if "id" not in session:
            return redirect("login")
        domains_thread = ThreadWithReturnValue(target=database.subdomains_from_token, args=(session["id"],))
        domains_thread.start()
        all_sub_domains_thread = ThreadWithReturnValue(target=CACHE_INSTANCE().get_subdomains)
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

            if (INPUT in domains_thread.join()) == False: #if user doesn't own domain, return them back
                return redirect("dashboard")


            if CLOUDFLARE()[DOMAIN].find_and_delete(INPUT):
                database.delete(subdomain=INPUT)
                send_discord_message(f"SESSION ID ``{target}`` as ``{get_github_username(github_id=target)}`` has **deleted** the domain: ``{INPUT}``.")
                domains_thread = ThreadWithReturnValue(target=CACHE_INSTANCE().get_subdomains, args=(True,))
                domains_thread.start()
                
            #return redirect("dashboard")



        user_info = user_info_thread.join().json()
        user_profile_picture = user_info["avatar_url"]
        user_company = user_info["company"]

        
        domains = domains_thread.join()
        if domains == []:
            return render_template(
                "dashboard.html",
                subdomains=[],
                github_username=session["username"],
                github_profile=user_profile_picture,
                github_company=user_company,
                response=response
            )
        
        all_sub_domains = all_sub_domains_thread.join()
        try:
            
                user_subdomains = [
                possible_domain
                for possible_domain in all_sub_domains
                if possible_domain["name"] in domains
            ]
        except Exception as e:
            print("ERROR ------------------------------\n"+e)
            user_subdomains = []

        return render_template(
            "dashboard.html",
            subdomains=user_subdomains,
            github_username=session["username"],
            github_profile=user_profile_picture,
            github_company=user_company,
            response=response
        )

    #ADMIN CODE
    #===============================
    #/loginadmin
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


    #/admin
    @app.route("/admin", methods=["GET", "POST"])  # admin site soon
    def admin():
        if not g.user:
            return redirect(url_for("adminlogin"))
        
        subdomains = ThreadWithReturnValue(target=cloudf_doms, args = (DOMAINS(),CLOUDFLARE(),))
        subdomains.start()

        owners = database.admin_fetchall()

        
        args = request.args.to_dict()
        if "delete" in args and args["delete"] is not None:

            INPUT = args["delete"]
            insert = INPUT.split(".")
            DOMAIN = insert[1] + "." + insert[2]

            if CLOUDFLARE()[DOMAIN].find_and_delete(INPUT):
                database.delete(subdomain=INPUT)
            
            target = session["admin_email"]
            send_discord_message(f":safety_vest: ADMIN ``{target}`` has deleted the domain ``{INPUT}``. :safety_vest: ")
            
            #re-run the code
            subdomains.join()
            subdomains = ThreadWithReturnValue(target=cloudf_doms, args = (DOMAINS(),CLOUDFLARE(),)) #re-run it
            subdomains.start()
        
        elif "disassociate" in args and args["disassociate"] is not None:
            DOMAIN_TO_REMOVE = args["disassociate"]
            database.delete(subdomain=DOMAIN_TO_REMOVE)
            target = session["admin_email"]
            send_discord_message(f":safety_vest: ADMIN ``{target}`` has modified the SQL; Disassociated the domain ``{DOMAIN_TO_REMOVE}``. :safety_vest: ")
            owners = database.admin_fetchall()

        x = subdomains.join()

        return render_template(
            "admin.html", subdomains=x, len_sd = len(x), account_id=CLOUDFLARE_ACCOUNT_ID, owners=owners, len_owners=len(owners)
        )

    #Before a Website is Accessed
    #BEFORE_REQUEST
    #Only /admin and /loginadmin really uses this
    #======================================
    @app.before_request
    def before_request():
        g.user = None
        if "user_id" in session:
            user = [x for x in ADMIN_ACCTS if x.id == session["user_id"]][0]
            g.user = user
        

    #After A Website is Accessed
    #AFTER_REQUEST
    #=======================================
    @app.after_request
    def after_request_func(response):
        if session.get("id") != None:
            try:
                target = session.get("id")
                if request.path.count('/') == 1:
                    send_discord_message(f"Session ``{target}`` as ``{get_github_username(github_id=target)}`` accessed the subdirectory ``{request.path}``")
            except:
                pass
            
        return response

    # ERROR HANDLING
    # Goes to another website and prints issue
    #=======================================
    if not DEBUG_MODE:
        @app.errorhandler(Exception)
        def handle_error(error):
            import sys
            exc_type, exc_value, exc_traceback = sys.exc_info()
            error_message = f"An error occurred: {exc_type} - {exc_value}"
            try:
                target = session["id"]
            except:
                return render_template("error.html", error=error_message)
            Thread(target=send_discord_message, args = (f"SESSION ID ``{target}`` as ``{get_github_username(github_id=target)}`` has encountered an error: ``{error_message}``",)).start()
            return render_template("error.html",error=error_message)
        
    
    return app


#STARTUP
#Sets up Cache ahead of time
def startup():
    t = Thread(target=CACHE_INSTANCE().get_subdomains, args=(False,))
    t.start()
    print("SERVER STARTED...")
    send_discord_message("SERVER STARTING!")
    t.join()
    print("Cache is up to date!")
    send_discord_message("Cache up to date.")
    

if __name__ == "__main__":
    startup()
    app = define_app()
    app.register_blueprint(authentication())
    
    if DEBUG_MODE:
        app.run(host="0.0.0.0", port=PORT, debug=DEBUG_MODE, threaded=True)
    else:
        try:
            from waitress import serve
            serve(app, host="0.0.0.0", port=PORT)
        except:
            app.run(host="0.0.0.0", port=PORT, debug=False, threaded=True)