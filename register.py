import requests
import json

class Cloudflare:
    def __init__(self, api_token, account_id, zone_id):
        self.API_TOKEN = api_token
        self.ACCOUNT_ID = account_id
        self.ZONE_ID = zone_id


cloudflare = Cloudflare("your-api-token","your-account-id","your-zone-id")

# Set the DNS record details
DNS_RECORD_NAME = "example.com"
DNS_RECORD_TYPE = "A"
DNS_RECORD_CONTENT = "192.168.1.1"
TTL = 1  # Time to Live in seconds
PROXIED = False

# Create the DNS record data
dns_record_data = {
    "type": DNS_RECORD_TYPE,
    "name": DNS_RECORD_NAME,
    "content": DNS_RECORD_CONTENT,
    "ttl": TTL,
    "proxied": PROXIED
}

# Set the API endpoint URL
url = f"https://api.cloudflare.com/client/v4/zones/{cloudflare.ZONE_ID}/dns_records"

# Set headers with the API token and content type
headers = {
    "Authorization": f"Bearer {cloudflare.API_TOKEN}",
    "Content-Type": "application/json"
}

# Send a POST request to add the DNS record
response = requests.post(url, headers=headers, data=json.dumps(dns_record_data))

# Check the response
if response.status_code == 200:
    print("DNS record added successfully.")
    print("Response:", response.json())
else:
    print("Failed to add DNS record.")
    print("Status Code:", response.status_code)
    print("Response:", response.text)