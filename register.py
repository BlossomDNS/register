import requests
import json

class Cloudflare:
    def __init__(self, api_token, account_id, zone_id):
        self.API_TOKEN = api_token
        self.ACCOUNT_ID = account_id
        self.ZONE_ID = zone_id

        self.headers = {
            "Authorization": f"Bearer {self.API_TOKEN}",
            "Content-Type": "application/json"
        }
    
    def insert_A_record(self, DNS_RECORD_NAME:str, DNS_RECORD_CONTENT: str, TTL:int = 1, PROXIED: bool = False):
        dns_record_data = {
            "type": "A",
            "name": DNS_RECORD_NAME,
            "content": DNS_RECORD_CONTENT,
            "ttl": TTL,
            "proxied": PROXIED
        }
        self.execute(dns_record_data=dns_record_data)

    def insert_CNAME_record(self, DNS_RECORD_NAME:str, DNS_RECORD_CONTENT: str, TTL:int = 1, PROXIED: bool = False):
        dns_record_data = {
            "type": "CNAME",
            "name": DNS_RECORD_NAME,
            "content": DNS_RECORD_CONTENT,
            "ttl": TTL,
            "proxied": PROXIED
        }
        self.execute(dns_record_data=dns_record_data)
    
    def execute(self, dns_record_data):
        url = f"https://api.cloudflare.com/client/v4/zones/{self.ZONE_ID}/dns_records"
        response = requests.post(url, headers=self.headers, data=json.dumps(dns_record_data))

        # Check the response
        if response.status_code == 200:
            print("DNS record added successfully.")
            print("Response:", response.json())
        else:
            print("Failed to add DNS record.")
            print("Status Code:", response.status_code)
            print("Response:", response.text)

        


cloudflare = Cloudflare("your-api-token","your-account-id","your-zone-id")


cloudflare.insert_A_record(DNS_RECORD_NAME="example.com", DNS_RECORD_CONTENT="192.168.1.1")

#TTL = 1  # Time to Live in seconds
#PROXIED = False
