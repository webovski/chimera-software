import json
import aiohttp

PRODUCT = 'comments-parser'
API_KEY = 'AKfycbx3Jbta9wORiwK_lPZS5UrbSdFlo718lTX9rIyTEZQbDnibW3DuZ0IlVR4vAesaUbL_gw'
API_URL = 'https://script.google.com/macros/s/{}/exec?product={}&userData={}&ip={}&country={}'


async def get_request_api(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            text = await resp.text()
            return text


async def geo_client_info():
    try:
        response = await get_request_api('https://api.myip.com')
        api_result = json.loads(response)
        ip = api_result['ip']
        country = api_result['country']

        return [ip, country]

    except Exception:
        return ['0.0.0.0', 'UNKNOWN']


async def check_licence(login: str, password: str):
    try:
        client_info = await geo_client_info()

        client_ip = client_info[0]
        client_country = client_info[1]
        api_text = await get_request_api(API_URL.format(API_KEY, PRODUCT, f'{login}:{password}', client_ip, client_country))
        print(json.loads(api_text)['response'])
        if json.loads(api_text)['response']:
            return True

        return False
    except Exception:
        return False
