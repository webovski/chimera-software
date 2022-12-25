import asyncio
from pathlib import Path

import async_eel
from core.helpers.telegram import TelethonCustom

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
    else:
        asyncio.run(start_accounts(sessions))

