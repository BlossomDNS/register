from concurrency import *
from main import CLOUDFLARE
from config import CLOUDFLARE_DOMAINS

class Cache():
    def __init__(self) -> None:
        self.all_sub_domains = []
        
    def get_subdomains(self):
        if self.all_sub_domains == []:
            all_domains = cloudf_doms(CLOUDFLARE_DOMAINS, CLOUDFLARE)
            self.all_sub_domains = all_domains
            return all_domains