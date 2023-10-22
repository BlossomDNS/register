from flask import render_template
import requests


def get_pr_date():
    url = 'https://api.github.com/repos/LunesDomainProject/register/pulls'

    response = requests.get(url)


    if response.status_code == 200:
        pulls_data = response.json()

        open_pr = [pull['html_url'] for pull in pulls_data] 
        return open_pr

    else:
        print(f"Request failed with status code {response.status_code}")


def load_github_sites(app):
    @app.route('/pr')
    def pr():
        links = get_pr_date()

        return render_template('github.html', links = links, n = len(links))