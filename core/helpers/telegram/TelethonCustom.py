from telethon import TelegramClient
from telethon.sessions import Session
from typing import Union

from core.System import ProxyManagment
from core.System import JsonWriteReader


async def create_client(session: Union[str, Session]) -> TelegramClient:
    json_path = session.replace('session', 'json')
    account_json = await JsonWriteReader.read_account_json(json_path)
    # account_proxy = account_json.get('proxy') connect throw account default proxy if turned on in settings
    account_proxy = await ProxyManagment.get_random_proxy()
    # console.info(f"Connected via proxy: {account_proxy['addr']}", severe=True)
    return TelegramClient(session,
                          api_id=account_json.get('api_id'),
                          api_hash=account_json.get('api_hash'),
                          device_model=account_json.get('device_model'),
                          system_version=account_json.get('system_version'),
                          app_version=account_json.get('app_version'),
                          lang_code=account_json.get('lang_code'),
                          system_lang_code=account_json.get('system_lang_code'),
                          proxy=('socks5',
                                 account_proxy['addr'],
                                 account_proxy['port'],
                                 True,  # with authentication,
                                 account_proxy['username'],
                                 account_proxy['password'],),
                          connection_retries=0)
