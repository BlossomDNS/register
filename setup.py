import os.path
import config
import json 

#this code has to do with setting up server for first time

def setup() -> int:
    if os.path.exists("subdomains.json"):
        return 0
    else:
        dict = {}
        for x in config.cloudflare_domain:
            print(x)
            dict[x] = {}
        
        # Writing to sample.json
        with open("subdomain.json", "w") as outfile:
            json.dump(dict, outfile, indent=4)
        return 0