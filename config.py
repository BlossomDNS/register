#Constants Variables

#github
GITHUB_REPO = "BlossomDNS/register"
GITHUB_SUBDOMAIN_JSON = f"https://raw.githubusercontent.com/{GITHUB_REPO}/main/subdomain.json"
#cloudflare
CLOUDFLARE_API_TOKEN = "zGhd0_Op4rOspGukhoYF1QdLMSgtwuL3ieMe_6hM"
CLOUDFLARE_ACCOUNT_ID = "59f63afb6cc56c945ee7e5e8becdc900"

#DNS Records publishing
PROXIED_ON = False
TTL_INT = 1
#domain you are giving subdomains away
CLOUDFLARE_DOMAINS = [{"url":"cool-web.site", "cloudflare_zone_id": "4d8a6c56a672891cc29c12ae8c3ad9c3"},
                    {"url":"pro-dev.app", "cloudflare_zone_id": "6f5f6beffb129ab68b3886ad746245ca"},
                    {"url":"pro-dev.site", "cloudflare_zone_id": "948989c30cb70f692bd7219a8fc8a5c0"},
                    {"url":"py-dev.io", "cloudflare_zone_id": "cb099786d5bc0dd52ef5d53530d5a122"}]
#admin
import admins
ADMIN_ACCTS = [
                admins.Admin(id=1, username="test@test", password="test"), 
                admins.Admin(id=2, username="test", password="test")
               ]
#git auth
CLIENT_SECRET = ""
CLIENT_ID = ""