#Constants Variables

#github
GITHUB_REPO = "BlossomDNS/register"
GITHUB_SUBDOMAIN_JSON = f"https://raw.githubusercontent.com/{GITHUB_REPO}/main/subdomain.json"
#cloudflare
CLOUDFLARE_API_TOKEN = ""
CLOUDFLARE_ACCOUNT_ID = ""
CLOUDFLARE_ZONE_ID = ""
#DNS Records publishing
PROXIED_ON = False
TTL_INT = 1
#domain you are giving subdomains away
CLOUDFLARE_DOMAIN = ["example.com","test.com"]
#admin
import admins
ADMIN_ACCTS = [
                admins.Admin(id=1, username="test@test", password="test"), 
                admins.Admin(id=2, usernmae="test", password="test")
               ]