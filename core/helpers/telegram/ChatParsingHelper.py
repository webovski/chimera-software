import asyncio
import json
import math
import os
import re
import string
from random import shuffle

from telethon import utils, functions
from telethon.tl.functions.messages import ImportChatInviteRequest
from telethon.tl.types import ChatInviteAlready
from telethon import types

import async_eel
from core.System import JsonWriteReader
from core.System.JsonWriteReader import edit_json
from core.helpers.ExcelHelper import create_excel_doc
from core.helpers.SQLiteHelper import close_connection
from core.helpers.telegram import TelethonCustom
from core.helpers.telegram.TelethonCustom import get_dialogs, build_user_status, parse_users
from core.helpers import SQLiteHelper

max_threads = 25
semaphore = asyncio.Semaphore(max_threads)

LATIN_ALPHABET = dict(zip(string.ascii_lowercase, range(1, 27)))
CYRILLIC_ALPHABET = ['а', 'б', 'в', 'г', 'д', 'е', 'ё', 'ж', 'з', 'и', 'й', 'к', 'л', 'м', 'н', 'о', 'п', 'р', 'с', 'т',
                     'у', 'ф', 'х', 'ц', 'ч', 'ш', 'щ', 'ъ', 'ы', 'ь', 'э', 'ю', 'я', '0', '1', '2', '3', '4', '5', '6',
                     '7', '8', '9', '_', '', '*']

ALPHABET = list(LATIN_ALPHABET.keys()) + CYRILLIC_ALPHABET
parser_iteration = 1


async def start_accounts(sessions, chunked_letters, connection, parameters: dict):
    coroutines = []
    global parser_iteration
    parser_iteration = 0
    for index, session in enumerate(sessions):
        try:
            coroutines.append(work_with_account(session, chunked_letters[index], parameters, connection))
        except IndexError:
            print(f"No tasks for account: {session}")
    await asyncio.gather(*coroutines)


async def work_with_account(session_path: str, target_letters: list, parameters: dict, connection):
    """logic for main scraping"""
    global parser_iteration

    dialog_parsing = parameters["dialogsParsing"]
    parse_premium = parameters["premium"]
    parse_phones = parameters["parsePhones"]
    parse_photos = parameters["onlyPhotos"]
    only_admins = parameters["parseOnlyAdmins"]
    only_bots = parameters["parseOnlyBots"]
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
                    if len(temp_) > 0:
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
                        parsed_users = await parse_users(client, target_letter, chat_entity, parse_admins=only_admins,
                                                         parse_bots=only_bots)

                        all_users = parsed_users.get('all_users')
                        bots = parsed_users.get('bots')
                        admins = parsed_users.get('admins')

                        for user in all_users:
                            if not user.last_name:
                                last_name = ''
                            else:
                                last_name = user.last_name
                            full_name = f'{user.first_name} {last_name}'
                            username = user.username
                            has_avatar = 1 if user.photo is not None else 0
                            was_online = await build_user_status(user)
                            phone = user.phone
                            is_premium = user.premium
                            is_scam = user.scam
                            is_bot = user.bot

                            save_user = True

                            if parse_photos and not phone:
                                save_user = False
                            if parse_premium and not is_premium:
                                save_user = False
                            if parse_photos and not has_avatar:
                                save_user = False
                            if parse_phones and not phone:
                                save_user = False
                            if only_bots and not user.bot:
                                save_user = False

                            if save_user:
                                await SQLiteHelper.insert_parsed_user(connection, user.id,
                                                                      full_name,
                                                                      username, has_avatar,
                                                                      was_online, phone, 0,
                                                                      is_premium, is_scam, is_bot)

                        print(f'Percents: {int(100 * parser_iteration / len(ALPHABET))}%')
                        parser_iteration = parser_iteration + 1
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
            try:
                await client.disconnect()
            except:
                pass
            print(f'Unexpected | {session_path} {Unexpected}')


def all_done(connection):
    async_eel.displayToast(f'Парсинг завершен!', 'success')
    async_eel.unblockButton("clear-parsing-database")
    async_eel.unblockButton("download-parsing-results")
    close_connection(connection)
    loop = asyncio.get_running_loop()
    if loop and loop.is_running():
        # here can be some action like accounts refreshing, saving logs, etc
        pass
    else:
        # here can be some action like accounts refreshing, saving logs, etc
        pass


@async_eel.expose
async def run_parsing(accounts_names, parameters):
    try:
        # parameters it's settings with filters for scraping
        # check chats-parser js for read signature
        # print(parameters)
        fast_parsing = parameters["fastParsing"]
        only_admins = parameters["parseOnlyAdmins"]
        only_bots = parameters["parseOnlyBots"]

        input_sessions_folder = 'accounts/input/'
        connection = SQLiteHelper.get_connection()
        sessions = [f'{input_sessions_folder}{path}' for path in accounts_names]

        if not fast_parsing:
            letters_list = ALPHABET
            shuffle(letters_list)
        else:
            letters_list = [" "]
        if only_admins or only_bots:
            letters_list = [" "]
        chunk_size = math.ceil((len(letters_list) / len(sessions)))
        chunked_letters = [letters_list[i:i + chunk_size] for i in range(0, len(letters_list), chunk_size)]

        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = None

        print('Starting parsing!')

        if loop and loop.is_running():
            task = loop.create_task(start_accounts(sessions, chunked_letters, connection, parameters))
            task.add_done_callback(lambda t: all_done(connection))
            await task
        else:
            asyncio.run(start_accounts(sessions, chunked_letters, connection, parameters))
    except Exception as e:
        print(e)


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
            info_object = await client(functions.messages.CheckChatInviteRequest(hash=chat_entity))
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

@async_eel.expose
async def convert_db_to_excel():
    if os.path.exists('temp-parsing.db'):
        connection = SQLiteHelper.get_connection()
        query_set_users = SQLiteHelper.get_users(connection)
        result = create_excel_doc(query_set_users)
        close_connection(connection)
        if result is not None and not isinstance(result,Exception):
            async_eel.displayToast(f'Сохранение отчета в {result} завершено!', 'success')
        else:
            async_eel.displayToast(f'Сохранить отчет не удалось - {result}', 'error')



@async_eel.expose
async def remove_scraping_db():
    try:
        if os.path.exists('temp-parsing.db'):
            os.remove('temp-parsing.db')
            async_eel.displayToast(f'База парсинга очищена!', 'success')
    except Exception as e:
        print(f"error when try delete db parsing {e}")
