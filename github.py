import requests

url = 'https://api.github.com/repos/LunesDomainProject/register/pulls'


response = requests.get(url)


if response.status_code == 200:
    pulls_data = response.json()

    open_pr = [pull['html_url'] for pull in pulls_data] 
    print(open_pr)

else:
    print(f"Request failed with status code {response.status_code}")
