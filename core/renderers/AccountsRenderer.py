import glob
import os
import async_eel


@async_eel.expose
async def render_accounts_list():
    input_sessions_folder = 'accounts/input/'
    sessions = [f for f in glob.glob(f"{input_sessions_folder}*.session")]

    accounts_html = ''

    for session_path in sessions:
        session_name = os.path.basename(os.path.normpath(session_path))
        account_item = f'<tr id="tr_{session_name}">' \
                            f'<td>' \
                                f'{session_name}' \
                            f'</td>' \
                            f'<td>' \
                                f'<button class="btn btn-outline-info" id="{session_name}" onclick=checkAccount("{session_name}")>' \
                                    f'<span class="icon-padding-5">' \
                                        f'Проверка' \
                                    f'</span>' \
                                    f'<i class="fas fa-user"></i>' \
                                f'</button' \
                           f'</td>' \
                       f'</tr>'
        accounts_html += account_item

    if len(accounts_html) == 0:
        accounts_html = '<td class="text-center" colspan="2">Для начала работы поместите аккаунты в папку accounts/input</td>'

    async_eel.renderAccountsList(accounts_html)
    async_eel.displayToast(f'Список аккаунтов обновлён!<br/>Найдено сессий: {len(sessions)} ', 'success')


@async_eel.expose
async def render_dropdown_accounts_list():
    input_sessions_folder = 'accounts/input/'
    sessions = [f for f in glob.glob(f"{input_sessions_folder}*.session")]

    accounts_dropdown_html = '<option disabled selected>Выбор аккаунта</option>'

    for session_path in sessions:
        session_name = os.path.basename(os.path.normpath(session_path))
        account_item = f'<option>{session_name}</option>'
        accounts_dropdown_html += account_item

    async_eel.renderDropdownList(accounts_dropdown_html)
