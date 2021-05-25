import requests

def get_access_token():

    url = "https://appleid.apple.com/auth/oauth2/token/"

    params = {
        "client_id": "...",
        "client_secret": "...",
        "grant_type": "...",
        "scope": "..."
    }

    headers = {
        'Host': 'appleid.apple.com',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    kwargs = {
        "headers": headers,
        "params": params
    }

    res = requests.post(url, **kwargs)

    return res