#from concurrency import *

#from config import CLOUDFLARE_DOMAINS

#class Cache():
#    def __init__(self,CLOUDFLARE=None) -> None:
#        self.all_sub_domains = []
#        self.CLOUDFLARE = CLOUDFLARE
    
#    def setCloudflare(self, Cloudflare) -> None:
#        self.CLOUDFLARE = Cloudflare
        
#    def get_subdomains(self, force_refresh: bool=False):
#        if (self.all_sub_domains == []) or (force_refresh):
#            all_domains = cloudf_doms(CLOUDFLARE_DOMAINS, self.CLOUDFLARE)
#            self.all_sub_domains = all_domains
#            
#        print(self.all_sub_domains)
#            
#        return self.all_sub_domains
    
#    def force_get_subdomains(self):
#        #only use if we are in big shit
#        all_domains = cloudf_doms(CLOUDFLARE_DOMAINS, self.CLOUDFLARE)
#        self.all_sub_domains = all_domains
#        print(self.all_sub_domains)
#        return self.all_sub_domains
#    
#    def add_subdomain(self, subdomain):
#        self.all_sub_domains.append(subdomain)