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

        self.headers = {
            "Authorization": f"Bearer {self.API_TOKEN}",
            "Content-Type": "application/json"
        }
    
    def getDNSrecords(self) -> list:
        url = f"https://api.cloudflare.com/client/v4/zones/{self.ZONE_ID}/dns_records"

        response = requests.get(url, headers=self.headers)

        if response.status_code == 200:
            return json.loads(response.content)["result"]
            #return [{"type":pull["type"], "name":pull["name"],"content":pull["content"],"proxied":pull["proxied"], "ttl":pull["ttl"]} for pull in content]
        else:
            print("DIDN'T GET DNS RECORDS")
            print(response.text)

        return 
    
    #Most likely we won't use this. (clueless)
    def insert_A_record(self, DNS_RECORD_NAME:str, DNS_RECORD_CONTENT: str, PROXIED: bool = PROXIED_ON, comment:str = None):
        dns_record_data = {
            "type": "A",
            "name": DNS_RECORD_NAME,
            "content": DNS_RECORD_CONTENT,
            "proxied": PROXIED,
            "comment": comment
        }
        return self.execute(dns_record_data=dns_record_data) 
        

    def insert_CNAME_record(self, DNS_RECORD_NAME:str, DNS_RECORD_CONTENT: str, PROXIED: bool = PROXIED_ON, comment:str = None):
        dns_record_data = {
            "type": "CNAME",
            "name": DNS_RECORD_NAME, #the ___.site.com
            "content": DNS_RECORD_CONTENT, # target site
            "proxied": PROXIED,
            "comment": comment
        }
        return self.execute(dns_record_data=dns_record_data)
    
    def delete(self, identifier):
        url = f"https://api.cloudflare.com/client/v4/zones/{self.ZONE_ID}/dns_records/{identifier}"
        response = requests.delete(url, headers=self.headers)

        return response
    
    def execute(self, dns_record_data): #for post
        url = f"https://api.cloudflare.com/client/v4/zones/{self.ZONE_ID}/dns_records"
        response = requests.post(url, headers=self.headers, data=json.dumps(dns_record_data))

        return response
        
    def update_json(dns_record):
        with open("subdomain.json", "r") as jsonFile:
            data = json.load(jsonFile)

        data[dns_record["name"].split(".")[0]] = {"target":dns_record["content"],"type":dns_record["type"]}

        with open("subdomain.json", "w") as jsonFile:
            json.dump(data, jsonFile)
        


#inserts A_record
#cloudflare.insert_A_record(DNS_RECORD_NAME=cloudflare_url, DNS_RECORD_CONTENT="test."+cloudflare_url)
