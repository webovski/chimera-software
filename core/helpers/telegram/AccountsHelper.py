import asyncio
import json
import time
from pathlib import Path

from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError
from telethon.tl.patched import Message

import async_eel
from core.System import JsonWriteReader, ProxyManagment
from core.System.JsonWriteReader import edit_json
from core.helpers.telegram import TelethonCustom
from core.renderers.AccountsRenderer import render_accounts_list

max_threads = 25
semaphore = asyncio.Semaphore(max_threads)


async def start_accounts(sessions):
    coroutines = [work_with_account(path) for path in sessions]
    await asyncio.gather(*coroutines)


async def work_with_account(session_path: str):
    async with semaphore:
        try:
            client = await TelethonCustom.create_client(session_path)
            await client.connect()
            phone_number = session_path.rsplit('/', 1)[1].split('.')[0]

            json_path = session_path.replace('.session', '.json')

            session_file_path = f'{phone_number}.session'
            json_file_path = f'{phone_number}.json'
            if await client.is_user_authorized():
                me = await client.get_me()
                print(f"Valid {me.id} {me.username} | {session_path}")
                await client.send_message('me', 'Saved Messages')
                await client.disconnect()

                first_name = me.first_name
                last_name = ''
                username = 'null'
                phone = f'+{me.phone}'
                chimera_status = 'valid'

                if me.last_name:
                    last_name = me.last_name
                if me.username:
                    username = me.username

                json_path = session_path.replace('session', 'json')
                account_json = await JsonWriteReader.read_json(path=json_path)

                updated_json = {
                    'username': username,
                    'phone': phone,
                    'first_name': first_name,
                    'last_name': last_name,
                    'chimera_status': chimera_status
                }
                account_json.update(updated_json)
                await edit_json(json_path, account_json)


            else:
                print(f'Unauthorized | {session_path}')
                Path(session_path).rename(f"accounts/unauthorized/{session_file_path}")
                Path(json_path).rename(f"accounts/unauthorized/{json_file_path}")
        except Exception as Unexpected:
            print(f'Unexpected | {session_path} {Unexpected}')


def all_done(sessions):
    async_eel.displayToast(f'Проверка {len(sessions)} аккаунтов завершена!', 'success')
    async_eel.startRotating(0, 'false')
    async_eel.unblockButton('checking-accounts-btn', 'checking-accounts-btn-text', 'ПРОВЕРИТЬ АККАУНТЫ')

    loop = asyncio.get_running_loop()
    if loop and loop.is_running():
        loop.create_task(render_accounts_list(accounts_names=sessions))
    else:
        asyncio.run(render_accounts_list(accounts_names=sessions))


@async_eel.expose
async def check_accounts(accounts_names: list[str]):
    input_sessions_folder = 'accounts/input/'
    sessions = [f'{input_sessions_folder}{path.replace("tr_", "")}' for path in accounts_names]

    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:  # 'RuntimeError: There is no current event loop...'
        loop = None

    print('Starting accounts checking!')

    if loop and loop.is_running():
        task = loop.create_task(start_accounts(sessions))
        task.add_done_callback(
            lambda t: all_done(sessions))
        await task
    else:
        asyncio.run(start_accounts(sessions))


@async_eel.expose
async def get_sms_code(account_name: str):
    input_sessions_folder = 'accounts/input/'
    session_path = f'{input_sessions_folder}{account_name}'
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:  # 'RuntimeError: There is no current event loop...'
        loop = None
    if loop and loop.is_running():
        task = loop.create_task(run_get_sms(account_name, session_path))
        await task
    else:
        asyncio.run(run_get_sms(account_name, session_path))


async def run_get_sms(account_name: str, session_path: str):
    async with semaphore:
        try:
            client = await TelethonCustom.create_client(session_path)
            await client.connect()
            phone_number = session_path.rsplit('/', 1)[1].split('.')[0]

            json_path = session_path.replace('.session', '.json')

            session_file_path = f'{phone_number}.session'
            json_file_path = f'{phone_number}.json'
            if await client.is_user_authorized():
                me = await client.get_me()
                print(f"Valid {me.id} {me.username} | {session_path}")
                async_eel.displayToast(f'Аккаунт {phone_number} успешно подключен!', 'success')

                sms_bot_id = 777000
                chat = await client.get_entity(sms_bot_id)
                messages = await client.get_messages(chat, 1)
                if messages:
                    if isinstance(messages[0], Message):
                        message = messages[0].message
                        code = ""
                        for char in message:
                            if char.isdigit():
                                code += char
                            if char == ".":
                                break
                        if len(code) > 1:
                            async_eel.displayToast(f'Ваш код для авторизации {code}', 'success')
                        else:
                            # not found full code
                            async_eel.displayToast(f'Не удалось считать код..', 'error')
                    else:
                        # type of  object it's not  message
                        async_eel.displayToast(f'Не удалось считать код..', 'error')
                else:
                    # not found messages in chat
                    async_eel.displayToast(f'Не удалось считать код..', 'error')
                await client.disconnect()

            else:
                print(f'Unauthorized | {session_path}')
                async_eel.displayToast(f'Аккаунт {phone_number} не удалось подключить!', 'error')
                Path(session_path).rename(f"accounts/unauthorized/{session_file_path}")
                Path(json_path).rename(f"accounts/unauthorized/{json_file_path}")
            async_eel.unblockTableRow(account_name)
        except Exception as Unexpected:
            async_eel.unblockTableRow(account_name)
            print(f'Unexpected | {session_path} {Unexpected}')


@async_eel.expose
async def add_new_account(phone_number, sms_code=None, cloud_password=None, phone_code_hash=None):
    # here should be if for on/off proxies
    # right now we consider that proxy list is exists and proxies are valid
    api_id = 1
    api_hash = "b6b154c3707471f5339bd661645ed3d6"
    input_sessions_folder = 'accounts/input/'
    file_path = f'{input_sessions_folder}'
    try:
        random_proxy = await ProxyManagment.get_random_proxy()
        string_proxy_format = f"{random_proxy['addr']}:{random_proxy['port']}:{random_proxy['username']}:{random_proxy['password']}"
        client = TelegramClient(
            f"{file_path}{phone_number}",
            api_id=api_id,
            api_hash=api_hash,
            proxy=random_proxy,
            connection_retries=0
        )

        await client.connect()

        if not sms_code:
            if not await client.is_user_authorized():
                try:
                    sent_code_response = await client.send_code_request(phone_number)
                    phone_code_hash_from_telegram = sent_code_response.phone_code_hash
                    async_eel.setPhoneCodeHash(phone_code_hash_from_telegram)
                    async_eel.informUserAboutPhoneAdding('Код отправлен!', 'info')
                except Exception as AnyOtherExceptions:
                    async_eel.informUserAboutPhoneAdding(f'Произошла ошибка: {AnyOtherExceptions}', 'danger')
        else:
            print(phone_number, sms_code, cloud_password, phone_code_hash)
            try:
                result = await client.sign_in(
                    phone=phone_number,
                    code=sms_code,
                    phone_code_hash=phone_code_hash
                )
                user_info = await get_user_info(client)
                await client.disconnect()
                json_data = await generate_json_template(user_info,phone_number,api_id,api_hash,string_proxy_format)
                await edit_json(f"{file_path}{phone_number}.json",json_data)
                async_eel.informUserAboutPhoneAdding(f'Аккаунт успешно добавлен!', 'success')
                await render_accounts_list()
            except SessionPasswordNeededError:
                await client.sign_in(password=cloud_password)
                user_info = await get_user_info(client)
                await client.disconnect()
                json_data = await generate_json_template(user_info,phone_number,api_id,api_hash,string_proxy_format,cloud_password)
                await edit_json(f"{file_path}{phone_number}.json",json_data)
                async_eel.informUserAboutPhoneAdding(f'Аккаунт успешно добавлен!', 'success')
                await render_accounts_list()
    except Exception as AnyOtherGlobalException:
        print(AnyOtherGlobalException)
        async_eel.informUserAboutPhoneAdding(f'Что-то пошло не так: {AnyOtherGlobalException}', 'danger')

async def get_user_info(client: TelegramClient):
    user_info = await client.get_me()
    return user_info


async def generate_json_template(user_data,phone, api_id, api_hash, proxy, password=None):
    """create dict such as json config from account and connection information"""
    phone = f"{phone}"
    session_file = f"{phone}"
    register_time = int(time.time())
    last_check_time = int(time.time())
    first_name = f"{user_data.first_name}"
    last_name = f"{user_data.last_name if user_data.last_name is not None else ''}"
    username = f"{user_data.username if user_data.username is not None else 'null'}"
    twoFA = f"{password if password is not None else 'null'}"

    json_template = {
        "session_file": session_file,
        "phone": phone,
        "register_time": register_time,
        "app_id": api_id,
        "app_hash": api_hash,
        "sdk": "Android 9.0 Pie LG UX 7",
        "app_version": "3.50.68",
        "device": "Archos45Titanium",
        "last_check_time": last_check_time,
        "avatar": "null",
        "first_name": first_name,
        "last_name": last_name,
        "username": username,
        "sex": 0,
        "lang_pack": "ms",
        "system_lang_pack": "en-US",
        "proxy": [],
        "ipv6": False,
        "twoFA": twoFA,
        "chimera_status": "valid"
    }
    new_proxy_list = proxy.split(":")
    new_proxy = {
        'proxy': [3, str(new_proxy_list[0]), int(new_proxy_list[1]), True, new_proxy_list[2], new_proxy_list[3]]
    }
    json_template.update(new_proxy)
    return json_template
