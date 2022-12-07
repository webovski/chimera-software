import platform
from core.config.Common import start_eel

SYSTEM = platform.system()

if SYSTEM == 'Darwin':
    OS_INFO = {'slash': '/', 'os': 'MAC'}  # mac os
else:
    OS_INFO = {'slash': '\\', 'os': 'WIN'}  # windows


async def run_eel(os_type: str, source_template: str):
    await start_eel(source_template, os_type)
