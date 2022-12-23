import random

import async_eel
from core.System.JsonWriteReader import read_json, edit_json


async def load_proxies() -> list | None:
    """load proxies from txt file, if get error return None else return list"""
    path = "assets/proxies.txt"
    try:
        with open(path, mode="r", encoding="utf-8") as file_reader:
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
    print(json_paths)
    proxies = await load_proxies()
    if proxies is not None:
        if len(proxies) > 0:
            for json in json_paths:
                proxy = random.choice(proxies)
                await update_proxy(json, proxy)
            print("DONE")
        else:
            async_eel.displayToast(f'Прокси отсутствуют в файле proxies.txt', 'danger')

    else:
        async_eel.displayToast(f'Ошибка, не удалось прочитать прокси с файла', 'danger')


async def update_proxy(path: str, proxy: str):
    """update proxy in json file"""
    current_json = await read_json(path)
    if current_json is not None:
        # add logic for normal format proxy json
        current_json[proxy] = proxy
        await edit_json(path, current_json)
