from pprint import pprint

from telethon import TelegramClient
from telethon.sessions import Session
from typing import Union

from telethon.tl.functions.channels import GetParticipantsRequest
from telethon.tl.types import Channel, Chat, ChannelParticipantsSearch, ChannelParticipant, ChannelParticipantsAdmins

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


async def get_dialogs(client: TelegramClient):
    """get dialogs with type chat from account"""
    dialogs = await client.get_dialogs()
    return [dialog.entity for dialog in dialogs if
            isinstance(dialog.entity, Channel) or isinstance(dialog.entity, Chat)]


async def parse_users(client: TelegramClient, letter, target_group):
    all_participants = []

    offset = 0
    limit = 200
    my_filter = ChannelParticipantsSearch(letter)
    while_condition = True

    try:
        while while_condition:
            participants = await client(
                GetParticipantsRequest(channel=target_group, filter=my_filter, offset=offset, limit=limit, hash=0))

            all_participants.extend(participants.users)
            offset += len(participants.users)
            participants_count = len(participants.users)
            if participants_count < limit:
                while_condition = False
        return all_participants

    except Exception as AnyParsingException:
        print('Parsing Exception:', AnyParsingException)
        return all_participants


async def parse_admins(client: TelegramClient, target_group):
    all_participants = []

    offset = 0
    limit = 200
    my_filter = ChannelParticipantsAdmins()
    while_condition = True

    try:
        while while_condition:
            participants = await client(
                GetParticipantsRequest(channel=target_group, filter=my_filter, offset=offset, limit=limit, hash=0))

            all_participants.extend(participants.users)
            offset += len(participants.users)
            participants_count = len(participants.users)
            if participants_count < limit:
                while_condition = False
        return all_participants

    except Exception as AnyParsingException:
        print('Parsing Exception:', AnyParsingException)
        return all_participants


def build_user_status(status):
    if str(status) == "UserStatusRecently()":
        return "Заходил недавно"
    if str(status) == "UserStatusLastWeek()":
        return "Заходил на этой неделе"
    if str(status) == "UserStatusLastMonth()":
        return "Заходил в этом месяце"
    if "Online" in str(status):
        return status.expires.strftime("%d.%m.%Y, %H:%M")
    if "Offline" in str(status):
        return status.was_online.strftime("%d.%m.%Y, %H:%M")
    return "Заходил очень давно."
