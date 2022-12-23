import json


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


