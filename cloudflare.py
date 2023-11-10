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
            
        return self.all_sub_domains
    
    def force_get_subdomains(self):
        #only use if we are in big shit
        all_domains = cloudf_doms(CLOUDFLARE_DOMAINS, self.CLOUDFLARE)
        self.all_sub_domains = all_domains
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
        """
        Retrieves all cloudflare domains from specific ZONE

        Returns:
            list: All cloudflare domains from that specific ZONE
        """
        
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
        """
        Insert an 'A' DNS record into a DNS management system.

        Parameters:
        - DNS_RECORD_NAME (str): The name for the DNS record (e.g., "example.com").
        - DNS_RECORD_CONTENT (str): The content or IP address associated with the DNS record.
        - PROXIED (bool, optional): Whether the DNS record should be proxied or not. Default is PROXIED_ON.
        - comment (str, optional): A comment or description for the DNS record. Default is None.

        Returns:
        - response: The result of executing the DNS record insertion operation.

        This method allows you to insert an 'A' DNS record, which maps a hostname to an IPv4 address, into a DNS management system. You can specify the DNS record's name (hostname), content (IP address), and other optional parameters.

        The 'PROXIED' parameter determines whether the DNS record should be proxied through the DNS management system or not. Proxied DNS records typically benefit from features like DDoS protection and caching.

        The 'comment' parameter allows you to add an optional comment or description to the DNS record for reference purposes.

        Example Usage:
        ```
        # Insert a proxied 'A' DNS record for "example.com" with IP address "203.0.113.1" and a comment.
        response = insert_A_record("www.example.com", "203.0.113.1", True, "Web Server")
        ```

        """

        dns_record_data = {
            "type": "A",
            "name": DNS_RECORD_NAME,
            "content": DNS_RECORD_CONTENT,
            "proxied": PROXIED,
            "comment": comment,
        }
        return self.__execute(dns_record_data=dns_record_data)

    def insert_CNAME_record(
        self,
        DNS_RECORD_NAME: str,
        DNS_RECORD_CONTENT: str,
        PROXIED: bool = PROXIED_ON,
        comment: str = None,
    ):
        """
        Insert a 'CNAME' DNS record into a DNS management system.

        Parameters:
        - DNS_RECORD_NAME (str): The name for the DNS record (e.g., "subdomain.example.com").
        - DNS_RECORD_CONTENT (str): The target domain or hostname to which the CNAME record points.
        - PROXIED (bool, optional): Whether the DNS record should be proxied or not. Default is PROXIED_ON.
        - comment (str, optional): A comment or description for the DNS record. Default is None.

        Returns:
        - response: The result of executing the DNS record insertion operation.

        This method allows you to insert a 'CNAME' DNS record, which is used to alias one domain name to another. The 'CNAME' record maps a subdomain to a target domain or hostname.

        The 'DNS_RECORD_NAME' parameter specifies the name for the 'CNAME' record, which is typically a subdomain or alias of the main domain.

        The 'DNS_RECORD_CONTENT' parameter specifies the target domain or hostname to which the 'CNAME' record should point.

        The 'PROXIED' parameter determines whether the DNS record should be proxied through the DNS management system or not. Proxied DNS records typically benefit from features like DDoS protection and caching.

        The 'comment' parameter allows you to add an optional comment or description to the DNS record for reference purposes.

        Example Usage:
        ```
        # Insert a proxied 'CNAME' DNS record for "subdomain.example.com" pointing to "target-site.com" with a comment.
        response = insert_CNAME_record("subdomain.example.com", "target-site.com", True, "Website Alias")
        ```
        """
        dns_record_data = {
            "type": "CNAME",
            "name": DNS_RECORD_NAME,  # the ___.site.com
            "content": DNS_RECORD_CONTENT,  # target site
            "proxied": PROXIED,
            "comment": comment,
        }
        return self.__execute(dns_record_data=dns_record_data)


    def update(self, DNS_RECORD_NAME: str, DNS_RECORD_CONTENT: str, type: str, id: str, PROXIED: bool = PROXIED_ON, comment: str = None,):
        dns_record_data = {
            "type": type,
            "name": DNS_RECORD_NAME,  # the ___.site.com
            "content": DNS_RECORD_CONTENT,  # target site
            "proxied": PROXIED,
            "comment": comment,
        }
        """
        Update an existing DNS record in a DNS management system.

        Parameters:
        - DNS_RECORD_NAME (str): The name for the DNS record (e.g., "subdomain.example.com").
        - DNS_RECORD_CONTENT (str): The updated content or IP address associated with the DNS record.
        - type (str): The type of DNS record to update (e.g., "A" or "CNAME").
        - id (str): The unique identifier of the DNS record to be updated.
        - PROXIED (bool, optional): Whether the DNS record should be proxied or not. Default is PROXIED_ON.
        - comment (str, optional): A comment or description for the updated DNS record. Default is None.

        Returns:
        - response: The result of executing the DNS record update operation.

        This method allows you to update an existing DNS record in a DNS management system. You need to specify the DNS record's name, updated content, type, and the unique identifier (id) of the record you wish to update.

        The 'DNS_RECORD_NAME' parameter specifies the name of the DNS record, which is typically a subdomain or alias of the main domain.

        The 'DNS_RECORD_CONTENT' parameter specifies the updated content, such as the new IP address or target domain.

        The 'type' parameter specifies the type of DNS record you are updating (e.g., "A" or "CNAME").

        The 'id' parameter is a unique identifier for the DNS record to be updated, allowing the system to locate and modify the correct record.

        The 'PROXIED' parameter determines whether the DNS record should be proxied through the DNS management system or not. Proxied DNS records typically benefit from features like DDoS protection and caching.

        The 'comment' parameter allows you to add an optional comment or description to the updated DNS record for reference purposes.

        Example Usage:
        ```
        # Update an 'A' DNS record with the name "subdomain.example.com" to point to a new IP address and add a comment.
        response = update("subdomain.example.com", "203.0.113.2", "A", "record_id", True, "Updated IP Address")
        ```
        """
        return self.__put(dns_record_data=dns_record_data, id=id)


    def delete(self, identifier):
        url = f"https://api.cloudflare.com/client/v4/zones/{self.ZONE_ID}/dns_records/{identifier}"
        response = self.session.delete(url, headers=self.headers)
        
        CACHE_INSTANCE.get_subdomains(force_refresh=True)
        return response
    
    def find_and_delete(self, name: str) -> bool:
        """
        Find and delete a DNS record by its name in a DNS management system.

        Parameters:
        - name (str): The name of the DNS record to be found and deleted (e.g., "subdomain.example.com").

        Returns:
        - bool: True if the DNS record with the specified name is found and successfully deleted, False otherwise.

        This method allows you to search for a DNS record by its name and delete it from a DNS management system if it exists. It performs the following steps:

        1. Retrieves a list of DNS records using the `getDNSrecords` function.
        2. Iterates through the list of DNS records to find a record with a matching name.
        3. If a matching record is found, it attempts to delete the record using its identifier.
        4. Returns True if the record is successfully deleted (HTTP status code 200), and False if not.

        Example Usage:
        ```
        # Find and delete a DNS record with the name "subdomain.example.com."
        if find_and_delete("subdomain.example.com"):
            print("DNS record deleted successfully.")
        else:
            print("DNS record not found or deletion failed.")
        ```
        """
        x = self.getDNSrecords()

        for domain in x:
            if domain["name"]==name:
                if self.delete(identifier=domain["id"]).status_code == 200:
                    return True
                else:
                    return False
                
        return False
    
    def find(self, name:str) -> dict:
        """
        Find a DNS record by its name in a DNS management system.

        Parameters:
        - name (str): The name of the DNS record to be found (e.g., "subdomain.example.com").

        Returns:
        - dict: A dictionary representing the found DNS record, or None if no matching record is found.

        This method allows you to search for a DNS record by its name in a DNS management system. It performs the following steps:

        1. Retrieves a list of DNS records using the `getDNSrecords` function.
        2. Iterates through the list of DNS records to find a record with a matching name.
        3. Returns the dictionary representing the found DNS record if a match is found, or None if no matching record is found.

        Example Usage:
        ```
        # Find a DNS record with the name "subdomain.example.com."
        found_record = find("subdomain.example.com")
        
        if found_record:
            print("Found DNS record:", found_record)
        else:
            print("DNS record not found.")
        ```
        """
        x = self.getDNSrecords()

        for domain in x:
            if domain["name"]==name:
                return domain
                 
    def __execute(self, dns_record_data):  # for post

        url = f"https://api.cloudflare.com/client/v4/zones/{self.ZONE_ID}/dns_records"
        response = self.session.post(
            url, headers=self.headers, data=json.dumps(dns_record_data)
        )
        yes = Thread(target=CACHE_INSTANCE.get_subdomains, args=(True,))
        yes.start()

        yes.join()
        return response

    def __put(self, id, dns_record_data):
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