import asyncio
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
    try:
        random_proxy = await ProxyManagment.get_random_proxy()

        client = TelegramClient(
            phone_number,
            api_id=1,
            api_hash="b6b154c3707471f5339bd661645ed3d6",
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
            except SessionPasswordNeededError:
                await client.sign_in(password=cloud_password)
                await client.disconnect()
                async_eel.informUserAboutPhoneAdding(f'Аккаунт успешно добавлен!', 'success')
    except Exception as AnyOtherGlobalException:
        async_eel.informUserAboutPhoneAdding(f'Что-то пошло не так: {AnyOtherGlobalException}', 'danger')