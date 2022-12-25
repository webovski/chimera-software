import random

import async_eel
from core.System.JsonWriteReader import read_json, edit_json
from core.renderers import AccountsRenderer

PROXY_PATH = 'assets/proxies.txt'


async def get_random_proxy():
    proxy_details = random.choice(list(open(PROXY_PATH))).rstrip().split(sep=":")

    return {
        "proxy_type": "socks5",
        "addr": proxy_details[0],
        "port": int(proxy_details[1]),
        "username": proxy_details[2],
        "password": proxy_details[3]
    }

async def get_proxies() -> list | None:
    """load proxies from txt file, if get error return None else return list"""
    try:
        with open(PROXY_PATH, mode="r", encoding="utf-8") as file_reader:
            proxy_list = [proxy.strip("\n") for proxy in file_reader.readlines()]
            return proxy_list
    except Exception as e:
        print(f"error when try get proxies from file: {e}")
        return None


@async_eel.expose
async def set_proxies(accounts_names: list[str]):
    """main function for set proxies"""
    input_sessions_folder = 'accounts/input/'
    json_paths = [f'{input_sessions_folder}{path.replace("session", "json").replace("tr_", "")}' for path in
                  accounts_names]
    proxies = await get_proxies()
    if proxies is not None:
        setted_count = 0
        if len(proxies) > 0:
            for json in json_paths:
                proxy = random.choice(proxies)
                await update_proxy(json, proxy)
                setted_count += 1
            await AccountsRenderer.render_accounts_list(
                render_message=[f'{setted_count} прокси успешно установлены!', 'info'],
                accounts_names=accounts_names
            )
        else:
            async_eel.displayToast(f'Прокси отсутствуют в файле proxies.txt', 'danger')

    else:
        async_eel.displayToast(f'Ошибка, не удалось прочитать прокси с файла', 'danger')


async def update_proxy(path: str, proxy: str):
    """update proxy in json file"""
    try:
        current_json = await read_json(path)
        new_proxy_list = proxy.split(":")
        new_proxy = {'proxy': [3, str(new_proxy_list[0]), int(new_proxy_list[1]), True, new_proxy_list[2], new_proxy_list[3]]}
        current_json.update(new_proxy)
        await edit_json(path, current_json)

    except Exception as E:
        print(E)
