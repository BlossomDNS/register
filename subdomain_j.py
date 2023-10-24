import os.path

import requests
import config
import json 

#code that deals with the subdomain.json file

def setup() -> int:
    if os.path.exists("subdomains.json"):
        return 0
    else:
        dict = {}
        for x in config.cloudflare_domain:
            dict[x] = {}
        
        # Writing to sample.json
        with open("subdomain.json", "w") as outfile:
            json.dump(dict, outfile, indent=4)
        return 0


def retrieve_j():
    response = requests.get(config.github_subdomain_json)
    return response.content