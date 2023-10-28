#Constants Variables

#github
GITHUB_REPO = "BlossomDNS/register"
GITHUB_SUBDOMAIN_JSON = f"https://raw.githubusercontent.com/{GITHUB_REPO}/main/subdomain.json"
#cloudflare
CLOUDFLARE_API_TOKEN = "VnB5Y3ixxUBki4o5L9ZJqGFOE1Lx9qOgmiEY0orX"
CLOUDFLARE_ACCOUNT_ID = "9063adba3e67bd2d65acbaf4692a50b7"
CLOUDFLARE_ZONE_ID = "52ba56c16e9346a7f87abb9c6a42ef8e"
#DNS Records publishing
PROXIED_ON = False
TTL_INT = 1
#domain you are giving subdomains away
CLOUDFLARE_DOMAIN = ["example.com","test.com"]
#admin
import admins
ADMIN_ACCTS = [
                admins.Admin(id=1, username="test@test", password="test"), 
                admins.Admin(id=2, username="test", password="test")
               ]
#git auth
CLIENT_SECRET = ""
CLIENT_ID = ""