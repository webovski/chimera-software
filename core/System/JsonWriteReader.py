import json


async def read_account_json(json_file_path: str):
    with open(json_file_path) as file:
        account_json = json.load(file)
        accounts_setting_dict: dict = {
            'session': json_file_path.replace('.json', '.session'),
            'api_id': account_json.get('app_id'),
            'api_hash': account_json.get('app_hash'),
            'device_model': account_json.get('device'),
            'system_version': account_json.get('sdk'),
            'app_version': account_json.get('app_version'),
            'lang_code': account_json.get('lang_pack'),
            'system_lang_code': account_json.get('system_lang_pack'),
            'proxy': account_json.get('proxy'),
        }

    return accounts_setting_dict


async def read_json(path: str) -> dict | None:
    """read json if get error return None and print error, else return json dict"""
    try:
        with open(path, mode="r", encoding="utf-8") as file_reader:
            json_data = json.load(file_reader)
            return json_data
    except Exception as e:
        print(f"error when try read json from file: {e}")
        return None


async def edit_json(path: str, json_data: dict) -> bool:
    """write json dict to file if get error print error and return False, else True"""
    try:
        with open(path, mode="w", encoding="utf-8") as file_writer:
            json.dump(json_data, file_writer)
            return True
    except Exception as e:
        print(f"error when try write json file {e}")
        return False