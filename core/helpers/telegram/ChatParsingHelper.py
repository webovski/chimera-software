import asyncio
import math
import string
from random import shuffle

from telethon import utils, functions
from telethon.tl.functions.messages import ImportChatInviteRequest
from telethon.tl.types import ChatInviteAlready

import async_eel
from core.System import JsonWriteReader
from core.System.JsonWriteReader import edit_json
from core.helpers.telegram import TelethonCustom
from core.helpers.telegram.TelethonCustom import get_dialogs, parse_users

max_threads = 25
semaphore = asyncio.Semaphore(max_threads)

LATIN_ALPHABET = dict(zip(string.ascii_lowercase, range(1, 27)))
CYRILLIC_ALPHABET = ['а', 'б', 'в', 'г', 'д', 'е', 'ё', 'ж', 'з', 'и', 'й', 'к', 'л', 'м', 'н', 'о', 'п', 'р', 'с',
                     'т', 'у', 'ф', 'х', 'ц', 'ч', 'ш', 'щ', 'ъ', 'ы', 'ь', 'э', 'ю', 'я', '0', '1', '2', '3', '4',
                     '5', '6', '7', '8', '9', '_', '', '*']

ALPHABET = list(LATIN_ALPHABET.keys()) + CYRILLIC_ALPHABET


async def start_accounts(sessions, chunked_letters,  parameters: dict):
    coroutines = []

    for index, session in enumerate(sessions):
        try:
            coroutines.append(work_with_account(session, chunked_letters[index], parameters))
        except IndexError:
            print(f"No tasks for account: {session}")

    await asyncio.gather(*coroutines)


async def work_with_account(session_path: str, target_letters: list, parameters: dict):
    dialog_parsing = parameters["dialogsParsing"]
    need_premium = parameters["premium"]
    parse_phones = parameters["parsePhones"]
    without_admins = parameters["parseWithoutAdmins"]
    without_bots = parameters["parseWithoutBots"]
    chat = parameters["chat"]
    async with semaphore:
        try:
            client = await TelethonCustom.create_client(session_path)
            await client.connect()
            if await client.is_user_authorized():
                me = await client.get_me()
                print(f'Successfully connected: {me.phone}')
                if dialog_parsing:
                    dialogs = await get_dialogs(client)
                    temp_ = [dialog for dialog in dialogs if dialog.title == chat]
                    if len(temp_)>0:
                        chat_entity = temp_[0]
                    else:
                        raise Exception("Диалог с таким названием не найден!")
                else:
                    # get info about chat such as is_private and username
                    info_chat = await check_link(chat)
                    chat_entity = await get_entity_chat(client, info_chat)
                    if chat_entity is None:
                        raise Exception("Не удалось найти чат")

                for target_letter in target_letters:
                    try:
                        print(f'{session_path} | Symbol {target_letter}')
                        # parse users for target_latter
                        # adding to an array or directly insert into db
                        users = await parse_users(client, target_letter, chat_entity)
                        print(len(users))
                        pass
                    except Exception as AnyParsingException:
                        # display toast or another action
                        print(f'{session_path} | An error on symbol parsing occurred: {AnyParsingException}')
                        pass
                print(f'All done: {me.phone}')
                # after parsing here we will do something with parsed users or just disconnect account
                await client.disconnect()
            else:
                print(f'Unauthorized | {session_path}')
                updated_json = {'chimera_status': 'deleted'}
                json_path = session_path.replace('session', 'json')
                account_json = await JsonWriteReader.read_json(path=json_path)
                account_json.update(updated_json)
                await edit_json(json_path, account_json)
        except Exception as Unexpected:
            print(f'Unexpected | {session_path} {Unexpected}')


def all_done():
    async_eel.displayToast(f'Парсинг успешно завершен!', 'success')

    loop = asyncio.get_running_loop()
    if loop and loop.is_running():
        # here can be some action like accounts refreshing, saving logs, etc
        pass
    else:
        # here can be some action like accounts refreshing, saving logs, etc
        pass


@async_eel.expose
async def run_parsing(accounts_names,parameters):
    # parameters it's settings with filters for scraping
    # check chats-parser js for read signature
    # print(parameters)
    fast_parsing = parameters["fastParsing"]

    input_sessions_folder = 'accounts/input/'
    sessions = [f'{input_sessions_folder}{path}' for path in accounts_names]

    if not fast_parsing:
        letters_list = ALPHABET
        shuffle(letters_list)
    else:
        letters_list = [" "]
    chunk_size = math.ceil((len(letters_list) / len(sessions)))
    chunked_letters = [letters_list[i:i + chunk_size] for i in range(0, len(letters_list), chunk_size)]

    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None

    print('Starting parsing!')

    if loop and loop.is_running():
        task = loop.create_task(start_accounts(sessions, chunked_letters, parameters))
        task.add_done_callback(lambda t: all_done())
        await task
    else:
        asyncio.run(start_accounts(sessions, chunked_letters, parameters))


async def check_link(link):
    """check if link private and return is_private and entity in dict"""
    link = link.replace('/+', '/joinchat/') if '/+' in link else link
    result = utils.parse_username(link)

    return {"is_private": result[1], "entity": result[0]}


async def get_entity_chat(client, info_chat):
    """get entity by chat info contains is_private and entity"""
    chat_entity = info_chat["entity"]
    is_chat_private = info_chat["is_private"]
    try:
        if is_chat_private:
            info_object = await client(functions.messages.CheckChatInviteRequest(
                hash=chat_entity
            ))
            if not isinstance(info_object, ChatInviteAlready):
                update_object = await client(ImportChatInviteRequest(chat_entity))
                chat_entity = await client.get_entity(update_object.chats[0].id)
                return chat_entity
            else:
                chat_entity = await client.get_entity(info_object.chat)
                return chat_entity
        entity_for_scrap = await client.get_entity(chat_entity)
        return entity_for_scrap
    except Exception as e:
        print(f"Error when try get entity in function get_entity_chat:{e}")
        return None
