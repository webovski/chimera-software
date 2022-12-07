import async_eel
from core.handlers import StorageHanlder
from core.helpers import AuthHelper


@async_eel.expose
async def sign_in(login: str, password: str):
    async_eel.displayToast('Проверка вашей лицензии!', 'info', 'ui-button-id')
    authorized = await AuthHelper.check_licence(login, password)

    if authorized:
        async_eel.displayToast('Лицензия активна!', 'success', 'ui-button-id')
        async_eel.openApp()

        await StorageHanlder.init_directories()


    else:
        async_eel.displayToast('Лицензия не найдена!', 'error', 'ui-button-id')
        async_eel.backToLogin()
