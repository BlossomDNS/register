from concurrency import *
from cloudflare import *

from config import CLOUDFLARE_DOMAINS
CLOUDFLARE = {domain["url"]: Cloudflare(api_token=CLOUDFLARE_API_TOKEN, account_id=CLOUDFLARE_ACCOUNT_ID, zone_id=domain["cloudflare_zone_id"]) for domain in CLOUDFLARE_DOMAINS}


class Cache():
    def __init__(self) -> None:
        self.all_sub_domains = []
        
    def get_subdomains(self):
        if self.all_sub_domains == []:
            all_domains = cloudf_doms(CLOUDFLARE_DOMAINS, CLOUDFLARE)
            self.all_sub_domains = all_domains
            
        return self.all_sub_domains