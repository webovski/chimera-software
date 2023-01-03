from telethon import TelegramClient
from telethon.sessions import Session
from typing import Union
from telethon import types
from telethon.tl.functions.channels import GetParticipantsRequest
from telethon.tl.types import Channel, Chat, ChannelParticipantsSearch, ChannelParticipantsAdmins, \
    ChannelParticipantsBots, ChannelParticipantSelf, ChannelParticipant
from core.System import ProxyManagment
from core.System import JsonWriteReader


async def create_client(session: Union[str, Session]) -> TelegramClient:
    json_path = session.replace('session', 'json')
    account_json = await JsonWriteReader.read_account_json(json_path)
    # account_proxy = account_json.get('proxy') connect throw account default proxy if turned on in settings
    account_proxy = await ProxyManagment.get_random_proxy()
    # console.info(f"Connected via proxy: {account_proxy['addr']}", severe=True)
    return TelegramClient(session, api_id=account_json.get('api_id'), api_hash=account_json.get('api_hash'),
                          device_model=account_json.get('device_model'),
                          system_version=account_json.get('system_version'),
                          app_version=account_json.get('app_version'), lang_code=account_json.get('lang_code'),
                          system_lang_code=account_json.get('system_lang_code'),
                          proxy=('socks5', account_proxy['addr'], account_proxy['port'], True,  # with authentication,
                                 account_proxy['username'], account_proxy['password'],), connection_retries=0)


async def get_dialogs(client: TelegramClient):
    """get dialogs with type chat from account"""
    dialogs = await client.get_dialogs()
    return [dialog.entity for dialog in dialogs if
            isinstance(dialog.entity, Channel) or isinstance(dialog.entity, Chat)]


async def parse_users(client: TelegramClient, letter, target_group, parse_admins=False, parse_bots=False):
    all_participants = []

    if parse_bots:
        bots = await get_only_bots(client, target_group)
        me = await client.get_me()
        all_participants.extend(bots)
        print(f'{me.id} Bots are parsed!')
    if parse_admins:
        admins = await get_only_admins(client, target_group)
        me = await client.get_me()
        all_participants.extend(admins)
        print(f'{me.id} Admins are parsed!')

    if parse_bots or parse_admins:
        return {'all_users': all_participants}

    offset = 0
    limit = 200
    my_filter = ChannelParticipantsSearch(letter)
    while_condition = True

    try:
        while while_condition:
            participants = await client(
                GetParticipantsRequest(channel=target_group, filter=my_filter, offset=offset, limit=limit, hash=0))
            all_participants.extend(participants.users)
            admins = list(filter(
                lambda user: not isinstance(user, ChannelParticipantSelf) and not isinstance(user, ChannelParticipant),
                participants.participants))

            for user in participants.participants:
                if not isinstance(user, ChannelParticipantSelf) and not isinstance(user, ChannelParticipant):
                    admins.append(user)

            offset += len(participants.users)
            participants_count = len(participants.users)
            if participants_count < limit:
                while_condition = False

        return {'all_users': all_participants}

    except Exception as AnyParsingException:
        print('Parsing Exception:', AnyParsingException)
        return {'bots': bots, 'admins': admins, 'all_users': all_participants}


async def get_only_admins(client: TelegramClient, chat: str):
    admins = []
    try:
        async for admin in client.iter_participants(chat, filter=ChannelParticipantsAdmins()):
            admins.append(admin)
        return admins
    except Exception as ParsingAdminsException:
        print('Admin parsing exception:', ParsingAdminsException)
        return admins


async def get_only_bots(client: TelegramClient, chat: str):
    bots = []
    try:
        async for bot in client.iter_participants(chat, filter=ChannelParticipantsBots()):
            bots.append(bot)
        return bots
    except Exception as ParsingAdminsException:
        print('Bots parsing exception:', ParsingAdminsException)
        return bots


async def build_user_status(user):
    user_status = user.status

    if isinstance(user_status, types.UserStatusRecently):
        return "Заходил недавно"
    if isinstance(user_status, types.UserStatusLastWeek):
        return "Заходил на этой неделе"
    if isinstance(user_status, types.UserStatusLastMonth):
        return "Заходил в этом месяце"
    if isinstance(user_status, types.UserStatusOnline):
        return user_status.expires.strftime("%d.%m.%Y, %H:%M")
    if isinstance(user_status, types.UserStatusOffline):
        return user_status.was_online.strftime("%d.%m.%Y, %H:%M")
    if user.bot:
        return "Бот"

    return "Заходил очень давно."
