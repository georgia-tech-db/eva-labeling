"""
Contains code to connect to the Label Studio API and check the connection.
Will contain additional connection options in the future
"""

import configs
# Import the SDK and the client module
from label_studio_sdk import Client


# Connect to the Label Studio API and check the connection
def get_client():
    ls = Client(url=configs.LABEL_STUDIO_URL, api_key=configs.API_KEY)
    ls.check_connection()
    return ls