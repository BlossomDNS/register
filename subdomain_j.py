# import os.path

# import requests
# import config
# import json

# #code that deals with the subdomain.json file

# def setup() -> int:
#     if os.path.exists("subdomains.json"):
#         return 0
#     else:
#         dict = {}
#         for x in config.CLOUDFLARE_DOMAINS:
#             dict[x] = {}

#         # Writing to sample.json
#         with open("subdomain.json", "w") as outfile:
#             json.dump(dict, outfile, indent=4)
#         return 0


# def retrieve_j() -> dict:
#     try:
#         response = requests.get(config.GITHUB_SUBDOMAIN_JSON)
#         content = json.loads(response.content)
#         return content
#     except:
#         return None


# def check(domain_target: str) -> str:
#     library = retrieve_j()
#     if library == None:
#         return "Error in Retrieving Subdomain.json"

#     domain = domain_target.split(".")
#     if len(domain) != 3:
#         return "Bad Input"

#     try:
#         content = library[domain[1]+"."+domain[2]][domain[0]]
#     except:
#         return "Not Taken."

#     return "The user " + content["owner"] + " owns it."
