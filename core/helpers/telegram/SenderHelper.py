import asyncio
import math
import os
import sqlite3

import async_eel
from core.System import JsonWriteReader
from core.System.JsonWriteReader import edit_json
from core.helpers.SQLiteHelper import close_connection
from core.helpers.telegram import TelethonCustom
from core.helpers import SQLiteHelper

max_threads = 25
semaphore = asyncio.Semaphore(max_threads)


async def start_accounts(sessions, chunked_users, connection, parameters: dict):
    coroutines = []
    for index, session in enumerate(sessions):
        try:
            coroutines.append(work_with_account(session, chunked_users[index], parameters, connection))
        except IndexError:
            print(f"No tasks for account: {session}")
    await asyncio.gather(*coroutines)


async def work_with_account(session_path: str, target_users: list, parameters: dict, connection: sqlite3.Connection,
        connection_retries: int = 3):
    # getting sending parameters
    # dialog_parsing = parameters["dialogsParsing"]

    async with semaphore:
        try:
            client = await TelethonCustom.create_client(session_path)
            try:
                await client.connect()
            except Exception as AnyConnectionException:
                print(f'Left retries {connection_retries}: {AnyConnectionException}')
                if connection_retries > 0:
                    connection_retries -= 1
                    return await work_with_account(session_path, target_users, parameters, connection,
                                                   connection_retries)
                else:
                    print(f'Account {session_path} has been terminated in case of not connected state')
                    return False

            if await client.is_user_authorized():
                me = await client.get_me()
                print(f'Successfully connected: {me.phone}')
                async_eel.writeLog("result-users-sending-text-area", f"Аккаунт {me.phone} успешно подключен.")
                for target_user in target_users:
                    # sending logic
                    pass
                async_eel.writeLog("result-users-sending-text-area", f"Аккаунт {me.phone} закончил рассылку!")
                async_eel.autoScroll('result-users-sending-text-area')
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
            account_phone = session_path.rsplit('/', 1)[1].split('.')[0].replace("+", "")
            async_eel.writeLog("result-users-text-area",
                               f"Во время рассылки на аккаунте {account_phone} произошла ошибка: {Unexpected}")
            async_eel.autoScroll('result-users-sending-text-area')

            print(f'Unexpected | {session_path} {Unexpected}')


def all_done(connection):
    async_eel.displayToast(f'Расслка завершена!', 'success')
    close_connection(connection)
    loop = asyncio.get_running_loop()
    if loop and loop.is_running():
        # here can be some action like accounts refreshing, saving logs, etc
        pass
    else:
        # here can be some action like accounts refreshing, saving logs, etc
        pass


@async_eel.expose
async def run_sending(accounts_names, parameters):
    try:
        # here will be parameters from front end
        # sending = parameters["sending"]
        connection = SQLiteHelper.get_connection()

        input_sessions_folder = 'accounts/input/'
        sessions = [f'{input_sessions_folder}{path}' for path in accounts_names]

        target_users_list = ['@tathr', 'https://t.me/redcore']
        chunk_size = math.ceil((len(target_users_list) / len(sessions)))
        chunked_users = [target_users_list[i:i + chunk_size] for i in range(0, len(target_users_list), chunk_size)]

        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = None

        async_eel.writeLog("result-users-sending-text-area",
                           f"Рассылка запущена, подключаем аккаунты к API Telegram. Ожидайте!")
        async_eel.autoScroll('result-users-sending-text-area')

        if loop and loop.is_running():
            task = loop.create_task(start_accounts(sessions, chunked_users, connection, parameters))
            task.add_done_callback(lambda t: all_done(connection))
            await task
        else:
            asyncio.run(start_accounts(sessions, chunked_users, connection, parameters))
    except Exception as e:
        print(e)


@async_eel.expose
async def remove_scraping_db():
    try:
        if os.path.exists('temp-sending.db'):
            os.remove('temp-sending.db')
        async_eel.displayToast(f'База пользователей для рассылки очищена!', 'success')
    except Exception as e:
        print(f"error when try tp delete db sending {e}")
