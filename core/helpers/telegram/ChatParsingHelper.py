import asyncio
import math
import string
from random import shuffle

import async_eel
from core.System import JsonWriteReader
from core.System.JsonWriteReader import edit_json
from core.helpers.telegram import TelethonCustom

max_threads = 25
semaphore = asyncio.Semaphore(max_threads)

LATIN_ALPHABET = dict(zip(string.ascii_lowercase, range(1, 27)))
CYRILLIC_ALPHABET = ['а', 'б', 'в', 'г', 'д', 'е', 'ё', 'ж', 'з', 'и', 'й', 'к', 'л', 'м', 'н', 'о', 'п', 'р', 'с',
                     'т', 'у', 'ф', 'х', 'ц', 'ч', 'ш', 'щ', 'ъ', 'ы', 'ь', 'э', 'ю', 'я', '0', '1', '2', '3', '4',
                     '5', '6', '7', '8', '9', '_', '', '*']

ALPHABET = list(LATIN_ALPHABET.keys()) + CYRILLIC_ALPHABET


async def start_accounts(sessions, chunked_letters, chat):
    coroutines = []
    for index, session in enumerate(sessions):
        try:
            coroutines.append(work_with_account(session, chunked_letters[index], chat))
        except IndexError:
            print(f"No tasks for account: {session}")

    await asyncio.gather(*coroutines)


async def work_with_account(session_path: str, target_letters: list, chat: str):
    async with semaphore:
        try:
            client = await TelethonCustom.create_client(session_path)
            await client.connect()
            if await client.is_user_authorized():
                me = await client.get_me()
                print(f'Successfully connected: {me.phone}')
                for target_letter in target_letters:
                    try:
                        print(f'{session_path} | Symbol {target_letter}')
                        # parse users for target_latter
                        # adding to an array or directly insert into db
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
async def run_parsing(accounts_names: list[str], chat: str):
    input_sessions_folder = 'accounts/input/'
    sessions = [f'{input_sessions_folder}{path}' for path in accounts_names]

    letters_list = ALPHABET
    shuffle(letters_list)

    chunk_size = math.ceil((len(letters_list) / len(sessions)))
    chunked_letters = [letters_list[i:i + chunk_size] for i in range(0, len(letters_list), chunk_size)]

    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None

    print('Starting parsing!')

    if loop and loop.is_running():
        task = loop.create_task(start_accounts(sessions, chunked_letters, chat))
        task.add_done_callback(lambda t: all_done())
        await task
    else:
        asyncio.run(start_accounts(sessions, chunked_letters, chat))
