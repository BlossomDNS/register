import requests
from config import WEBHOOK_URL
from data_sql import dataSQL

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
        response = requests.post(WEBHOOK_URL, json=message, timeout=60)

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
        github_id (str): Session["id"] - connected to SQL

    Returns:
        str: The GitHub username if found, or None if the user is not found.
    """
    try:
        return dataSQL(dbfile="database.db").get_from_token(need="username", session=github_id)
    except Exception as e:
        print(f'An error occurred: {str(e)}')

    return None
