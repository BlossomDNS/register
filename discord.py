import requests
from config import WEBHOOK_URL

def send_discord_message(content):
    """
    Send a message to a Discord webhook.

    Args:
        content (str): The content of the message.

    Returns:
        bool: True if the message was sent successfully, False otherwise.
    """
    try:
        message = {'content': '**=======**\n'+content+'\n**=======**'}
        response = requests.post(WEBHOOK_URL, json=message)

        if response.status_code == 204:
            print('Message sent successfully to Discord!')
            return True
        else:
            print(f'Failed to send message. Status code: {response.status_code}')
            print(response.text)
            return False
    except Exception as e:
        print(f'An error occurred: {str(e)}')
        return False
    
def get_github_username(github_id):
    """
    Get the GitHub username of a user based on their GitHub ID.

    Args:
        github_id (str): The GitHub user ID.

    Returns:
        str: The GitHub username if found, or None if the user is not found.
    """
    try:
        # Create the GitHub API URL
        github_api_url = f'https://api.github.com/user/{github_id}'

        # Make an HTTP GET request to the GitHub API
        response = requests.get(github_api_url)

        if response.status_code == 200:
            user_info = response.json()
            return user_info.get('login')
        elif response.status_code == 404:
            print(f'GitHub user with ID {github_id} not found.')
        else:
            print(f'Failed to retrieve user information. Status code: {response.status_code}')
    except Exception as e:
        print(f'An error occurred: {str(e)}')

    return None