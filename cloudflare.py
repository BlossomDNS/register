"""

cloudflare.py

Contains cloudflare code for the program

Sending requests to cloudflare

"""

import requests
import json
from cloudflare import *
from config import *



class Cloudflare:
    def __init__(self, api_token, account_id, zone_id):
        self.API_TOKEN = api_token
        self.ACCOUNT_ID = account_id
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
        from cache import cache_instance
        cache_instance.get_subdomains(force_refresh=True)
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
        from cache import cache_instance
        cache_instance.add_subdomain(response.json())
        
        return response

    def put(self, id, dns_record_data):
        url = f"https://api.cloudflare.com/client/v4/zones/{self.ZONE_ID}/dns_records/{id}"
        response = self.session.put(
            url, headers=self.headers, data=json.dumps(dns_record_data)
        )
        return response


# inserts A_record
# cloudflare.insert_A_record(DNS_RECORD_NAME=cloudflare_url, DNS_RECORD_CONTENT="test."+cloudflare_url)
