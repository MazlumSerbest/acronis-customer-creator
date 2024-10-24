import os                         
import requests                   # used for sending requests to the API
from dotenv import load_dotenv    # used for reading the .env file
from base64 import b64encode

base_url = os.getenv('ACRONIS_API_V2_URL')

def get_token():
    load_dotenv()

    client_id = os.getenv('ACRONIS_CLIENT_ID')
    client_secret = os.getenv('ACRONIS_CLIENT_SECRET')
    
    encoded_client_creds = b64encode(f'{client_id}:{client_secret}'.encode('ascii'))
    
    basic_auth = {
        'Authorization': 'Basic ' + encoded_client_creds.decode('ascii')
    }
    
    response = requests.post(
        f'{base_url}/idp/token',
        headers={'Content-Type': 'application/x-www-form-urlencoded', **basic_auth},
        data={'grant_type': 'client_credentials'},
    )
    token_info = response.json()
    
    # print(token_info)
    return token_info
    
def get_auth():
    token_info = get_token()
    
    auth = {
        'Content-Type': 'application/json', 
        'Authorization': 'Bearer ' + token_info['access_token']
    }
    
    return auth