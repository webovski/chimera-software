import os
import sys
import async_eel

WINDOWS = 'WIN'


async def start_eel(source_template: str, os_type: str) -> async_eel:
    if os_type == WINDOWS:
        async_eel.browsers.set_path('electron', await set_resource_path('electron\\electron.exe'))
        return await async_eel.start(source_template, mode='custom', port=7255, cmdline_args=[
            await set_resource_path('electron\\electron.exe'), '.\main.js'
        ])

    return await async_eel.start(source_template, mode='electron', port=7255)


async def set_resource_path(rel_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, rel_path)
