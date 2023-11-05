from concurrency import *
from cloudflare import Cloudflare, CLOUDFLARE_API_TOKEN, CLOUDFLARE_API_TOKEN, CLOUDFLARE_ACCOUNT_ID

from config import CLOUDFLARE_DOMAINS
CLOUDFLARE = {domain["url"]: Cloudflare(api_token=CLOUDFLARE_API_TOKEN, account_id=CLOUDFLARE_ACCOUNT_ID, zone_id=domain["cloudflare_zone_id"]) for domain in CLOUDFLARE_DOMAINS}


class Cache():
    def __init__(self) -> None:
        self.all_sub_domains = []
        
    def get_subdomains(self, force_refresh: bool=False):
        if (self.all_sub_domains == []) or (force_refresh):
            all_domains = cloudf_doms(CLOUDFLARE_DOMAINS, CLOUDFLARE)
            self.all_sub_domains = all_domains
            
        print(self.all_sub_domains)
            
        return self.all_sub_domains
    
    def force_get_subdomains(self):
        #only use if we are in big shit
        all_domains = cloudf_doms(CLOUDFLARE_DOMAINS, CLOUDFLARE)
        self.all_sub_domains = all_domains
        print(self.all_sub_domains)
        return self.all_sub_domains
    
    def add_subdomain(self, subdomain):
        self.all_sub_domains.append(subdomain)

cache_instance = Cache()