"""

cloudflare.py

Contains cloudflare code for the program

Sending requests to cloudflare

"""

import requests
import json
from cloudflare import *
from concurrency import cloudf_doms
from config import *
from threading import Thread

from config import CLOUDFLARE_DOMAINS

class Cache():
    def __init__(self,CLOUDFLARE=None) -> None:
        self.all_sub_domains = []
        self.CLOUDFLARE = CLOUDFLARE
    
    def setCloudflare(self, Cloudflare) -> None:
        self.CLOUDFLARE = Cloudflare
        
    def get_subdomains(self, force_refresh: bool=False):
        if (self.all_sub_domains == []) or (force_refresh):
            all_domains = cloudf_doms(DOMAINS, self.CLOUDFLARE)
            self.all_sub_domains = all_domains
            
        print(self.all_sub_domains)
            
        return self.all_sub_domains
    
    def force_get_subdomains(self):
        #only use if we are in big shit
        all_domains = cloudf_doms(CLOUDFLARE_DOMAINS, self.CLOUDFLARE)
        self.all_sub_domains = all_domains
        print(self.all_sub_domains)
        return self.all_sub_domains
    
    def add_subdomain(self, subdomain):
        self.all_sub_domains.append(subdomain)
        

class Cloudflare:
    def __init__(self, api_token, zone_id):
        self.API_TOKEN = api_token
        self.ZONE_ID = zone_id
        self.session = requests.Session()

        self.headers = {
            "Authorization": f"Bearer {CLOUDFLARE_API_TOKEN}",
            "Content-Type": "application/json",
        }

    def getDNSrecords(self) -> list:
        url = f"https://api.cloudflare.com/client/v4/zones/{self.ZONE_ID}/dns_records"

        response = self.session.get(url, headers=self.headers)

        if response.status_code == 200:
            return json.loads(response.content)["result"]
        else:
            print("DIDN'T GET DNS RECORDS")

        return

    # Most likely we won't use this. (clueless)
    def insert_A_record(
        self,
        DNS_RECORD_NAME: str,
        DNS_RECORD_CONTENT: str,
        PROXIED: bool = PROXIED_ON,
        comment: str = None,
    ):
        dns_record_data = {
            "type": "A",
            "name": DNS_RECORD_NAME,
            "content": DNS_RECORD_CONTENT,
            "proxied": PROXIED,
            "comment": comment,
        }
        return self.execute(dns_record_data=dns_record_data)

    def insert_CNAME_record(
        self,
        DNS_RECORD_NAME: str,
        DNS_RECORD_CONTENT: str,
        PROXIED: bool = PROXIED_ON,
        comment: str = None,
    ):
        dns_record_data = {
            "type": "CNAME",
            "name": DNS_RECORD_NAME,  # the ___.site.com
            "content": DNS_RECORD_CONTENT,  # target site
            "proxied": PROXIED,
            "comment": comment,
        }
        return self.execute(dns_record_data=dns_record_data)


    def update(self, DNS_RECORD_NAME: str, DNS_RECORD_CONTENT: str, type: str, id: str, PROXIED: bool = PROXIED_ON, comment: str = None,):
        dns_record_data = {
            "type": type,
            "name": DNS_RECORD_NAME,  # the ___.site.com
            "content": DNS_RECORD_CONTENT,  # target site
            "proxied": PROXIED,
            "comment": comment,
        }
        return self.put(dns_record_data=dns_record_data, id=id)


    def delete(self, identifier):
        url = f"https://api.cloudflare.com/client/v4/zones/{self.ZONE_ID}/dns_records/{identifier}"
        response = self.session.delete(url, headers=self.headers)
        
        CACHE_INSTANCE.get_subdomains(force_refresh=True)
        return response
    
    def find_and_delete(self, name: str) -> bool:
        x = self.getDNSrecords()

        for domain in x:
            if domain["name"]==name:
                if self.delete(identifier=domain["id"]).status_code == 200:
                    return True
                else:
                    return False
                
        return False
    
    def find(self, name:str) -> dict:
        x = self.getDNSrecords()

        for domain in x:
            if domain["name"]==name:
                return domain
                 
    def execute(self, dns_record_data):  # for post

        url = f"https://api.cloudflare.com/client/v4/zones/{self.ZONE_ID}/dns_records"
        response = self.session.post(
            url, headers=self.headers, data=json.dumps(dns_record_data)
        )
        yes = Thread(target=CACHE_INSTANCE.get_subdomains, args=(True,))
        yes.start()

        yes.join()
        return response

    def put(self, id, dns_record_data):
        url = f"https://api.cloudflare.com/client/v4/zones/{self.ZONE_ID}/dns_records/{id}"
        response = self.session.put(
            url, headers=self.headers, data=json.dumps(dns_record_data)
        )
        yes = Thread(target=CACHE_INSTANCE.get_subdomains, args=(True,))
        yes.start()

        yes.join()
        return response
    
CLOUDFLARE = {domain["url"]: Cloudflare(api_token=CLOUDFLARE_API_TOKEN, zone_id=domain["cloudflare_zone_id"]) for domain in CLOUDFLARE_DOMAINS}
del CLOUDFLARE_DOMAINS
del CLOUDFLARE_API_TOKEN

CACHE_INSTANCE = Cache(CLOUDFLARE)
DOMAINS = set(CLOUDFLARE)