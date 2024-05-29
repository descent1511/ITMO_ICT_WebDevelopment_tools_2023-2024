import requests


def call_parse_url_api(github_url: str):
    api_url = "http://172.20.0.1:3000/parse-url/"
                
    data = {"url": github_url}
    print('ok')
    try:
        response = requests.post(api_url, json=data)
        if response.status_code != 200:
            print(f"Failed to call parse URL API. Status code: {response.status_code}, Response: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"An error occurred while calling parse URL API: {e}")

call_parse_url_api('https://github.com/descent1511')