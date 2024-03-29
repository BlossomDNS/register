from threadedreturn import ThreadWithReturnValue
from threading import Thread

'''
concurrency.py

Code here is designed to speed up certain processes that might take too long

'''
def cloudf_doms(DOMAINS, CLOUDFLARE) -> list:
    """
    Retrieve all subdomains for a list of domains using Cloudflare API.

    Parameters:
    - DOMAINS (list): A list of domain names for which subdomains are to be retrieved.
    - CLOUDFLARE (dict): A dictionary containing Cloudflare API objects for each domain.

    Returns:
    - list: A list of all subdomains for the specified domains.

    This function retrieves all subdomains for a list of domains using the Cloudflare API. It uses multi-threading to make concurrent requests for each domain, which can significantly improve efficiency.

    Parameters:
    - DOMAINS: A list of domain names (e.g., ["example.com", "sub.example.com"]).
    - CLOUDFLARE: A dictionary that maps domain names to Cloudflare API objects. Ensure that you have set up Cloudflare API objects with the necessary authentication information.

    Example Usage:
    ```
    # Define a list of domains and a dictionary of Cloudflare API objects.
    domains = ["example.com", "sub.example.com"]
    cloudflare_objects = {
        "example.com": cloudflare_api_object1,
        "sub.example.com": cloudflare_api_object2,
    }

    # Retrieve all subdomains for the specified domains.
    subdomains = cloudf_doms(domains, cloudflare_objects)
    
    # Print the list of subdomains.
    print("Subdomains:", subdomains)
    ```

    Note:
    - Ensure that you have Cloudflare API objects set up correctly in the `CLOUDFLARE` dictionary with the necessary authentication information.
    - The actual implementation of the `ThreadWithReturnValue` class and the `getDNSrecords` method is not provided in this code snippet and should be defined elsewhere.
    - The function returns a list of subdomains for the specified domains.
    """
    all_sub_domains = []
    records_threads = {}
    i=0
    for all_domain in DOMAINS:
        
        records_threads[i] = ThreadWithReturnValue(target = CLOUDFLARE[all_domain].getDNSrecords)
        records_threads[i].start()
        i+= 1
    
    for i in range(len(records_threads)):
        records = records_threads[i].join()
        for record in records:
            all_sub_domains.append(record)
        
        
    return all_sub_domains