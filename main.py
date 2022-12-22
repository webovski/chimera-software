import async_eel
import asyncio
from core.config import System
from core.handlers import AuthHandler
from core.handlers.StorageHanlder import init_directories
from core.renderers import AccountsRenderer

loop = asyncio.get_event_loop()


async def main():
    try:

        os_type = System.OS_INFO['os']
        await init_directories()
        await System.run_eel(os_type, 'app.html')
        async_eel.init('web')

    except Exception as AnyError:
        print(AnyError)


if __name__ == '__main__':
    asyncio.run_coroutine_threadsafe(main(), loop)
    loop.run_forever()
