from flask import render_template
import requests
from datetime import datetime


def get_pr_date():
    url = 'https://api.github.com/repos/LunesDomainProject/register/pulls'

    response = requests.get(url)


    if response.status_code == 200:
        pulls_data = response.json()

        return pulls_data
        open_pr = [pull['html_url'] for pull in pulls_data] 
        return open_pr

    else:
        print(f"Request failed with status code {response.status_code}")


def load_github_sites(app):
    @app.route('/pr')
    def pr():
        date_format = "%Y-%m-%dT%H:%M:%SZ"
        pulls_data = get_pr_date()
        links = [{"title":pull["title"], "url": pull['html_url'], "date": datetime.strptime(pull['created_at'], date_format).strftime("%Y-%m-%d")} for pull in pulls_data]


        return render_template('github.html', links = links, n = len(links))