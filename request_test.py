import requests
import settings
import pandas as pd


proxies = {'http': None, 'https': None}
headers = {
            'Content-Type': 'application/json',
            "Authorization": f'Api-Key {settings.API_KEY}'
        }

try:
    response = requests.get(
        settings.API_OPERATOR_URL,
        proxies=proxies,
        headers=headers,
        timeout=10
    )
    if response.ok:
        data = response.json()
        df = pd.json_normalize(data)
        print(df)
    else:
        print(f'Error: {response.status_code} - {response.text}')

except requests.exceptions.RequestException as e:
    print(f'Request failed:{e}')
