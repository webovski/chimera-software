import glob
import json
import os
import async_eel
import pathlib
import shutil
from itertools import chain
from datetime import datetime, date

async def read_account_json(json_file_path: str):
    try:
        with open(json_file_path) as file:
            account_json = json.load(file)
            accounts_setting_dict: dict = {
                'session_file': json_file_path.replace('.json', '.session'),
                'phone': account_json.get('phone'),
                'api_id': account_json.get('app_id'),
                'api_hash': account_json.get('app_hash'),
                'device_model': account_json.get('device'),
                'system_version': account_json.get('sdk'),
                'app_version': account_json.get('app_version'),
                'lang_code': account_json.get('lang_pack'),
                'register_time': account_json.get('register_time'),
                'username': account_json.get('username'),
                'first_name': account_json.get('first_name'),
                'last_name': account_json.get('last_name'),
                'chimera_status': account_json.get('chimera_status'),
                'sex': account_json.get('sex'),
                'proxy': account_json.get('proxy'),
                'system_lang_code': account_json.get('system_lang_pack')
            }

        return [True, accounts_setting_dict]
    except Exception as AccountJsonReadingError:
        print(f'AccountJsonReadingError: {AccountJsonReadingError}')
        return [False, {}]

@async_eel.expose
async def render_accounts_list(render_message=None, accounts_names=[]):
    input_accounts_names = accounts_names
    accounts_names = []
    for account_name in input_accounts_names:
        new_account_name = account_name.split('/')[-1]
        accounts_names.append(new_account_name)

    try:
        input_sessions_folder = 'accounts/input/'
        sessions = [f for f in glob.glob(f"{input_sessions_folder}*.session")]
        accounts_html = ''

        accounts_all = 0
        accounts_valid = 0
        accounts_not_checked = 0
        accounts_spam_block = 0

        for session_path in sessions:

            try:
                json_path = session_path.replace('session', 'json')
                account_json_config = await read_account_json(json_path)

                phone_number = account_json_config[1]['phone']
                gender = account_json_config[1]['sex']
                account_proxy = f'{account_json_config[1]["proxy"][1]}:{account_json_config[1]["proxy"][2]}'
                username = account_json_config[1]["username"]
                chimera_status = account_json_config[1]["chimera_status"]

                first_name = account_json_config[1]["first_name"]
                last_name = account_json_config[1]["last_name"]
                today = date.today()
                current_date = today.strftime("%d-%m-%Y")
                account_created_at = datetime.utcfromtimestamp(int(account_json_config[1]['register_time'])).strftime('%d-%m-%Y')

                current_d = datetime.strptime(current_date, "%d-%m-%Y")
                reg_d = datetime.strptime(account_created_at, "%d-%m-%Y")
                register_time_in_days = f'{current_d - reg_d}'.split(' ')[0]



                user_fl_names = f'{first_name} {last_name}'

                if chimera_status is None:
                    accounts_not_checked += 1
                    chimera_status = ['info', 'Аккаунт ещё не был использован в программе', 'Не проверен']
                elif chimera_status == 'valid':
                    accounts_valid += 1
                    chimera_status = ['success', 'Аккаунт готов к работе', 'Проверен']
                elif chimera_status == 'spam-block':
                    accounts_spam_block += 1
                    chimera_status = ['danger', 'Аккаунт ограничен', 'Спам-Блок']
                elif chimera_status == 'deleted':
                    chimera_status = ['danger', 'Аккаунт удалён', 'Удалён']
                else:
                    chimera_status = ['default', 'Не удалось распознать', 'Неизвестно']

                if gender == 0:
                    account_picture = 'https://icons-for-free.com/iconfiles/png/512/female+person+user+woman+young+icon-1320196266256009072.png'
                    readable_gender = 'Женщина'
                else:
                    account_picture = 'https://cdn1.iconfinder.com/data/icons/user-pictures/101/malecostume-512.png'
                    readable_gender = 'Мужчина'
            except Exception as E:
                print(E)
                phone_number = '+777000'
                readable_gender = 'Неизвестно'
                account_picture = 'https://cdn1.iconfinder.com/data/icons/user-pictures/100/unknown-512.png'
                account_proxy = '0.0.0.0'
                username = 'Неизвестно'
                chimera_status = ['danger', 'Ошибка чтнеия аккаунта', 'Ошибка']
                user_fl_names = 'Неизвестно'
                register_time_in_days = 'NaN дней'

            accounts_all += 1
            session_name = os.path.basename(os.path.normpath(session_path))
            account_item = f'<tr id="tr_{session_name}">' \
                                f'<td>' \
                                    f'<div class="form-check">' \
                                        f'<input class="form-check-input" type="checkbox" {"checked" if session_name in accounts_names  else ""} value="{session_name}"/>' \
                                    f'</div>' \
                                f'</td>' \
                                f'<td>' \
                                    f'<div class="d-flex align-items-center">'\
                                        f'<img alt="" class="rounded-circle account-picture" src="{account_picture}"></>'\
                                        f'<div class="ms-3">' \
                                            f'<p class="fw-bold mb-1 overflow-hidden-p">{user_fl_names}</p>'\
                                            f'<p class="text-muted mb-0 overflow-hidden-p">@{username}</p>' \
                                        f'</div>'\
                                    f'</div>'\
                                f'</td>'\
                                f'<td>' \
                                    f'<p class="fw-normal mb-1">{phone_number}</p>'\
                                    f'<p class="text-muted mb-0">{readable_gender}</p>'\
                                f'</td>' \
                                f'<td>' \
                                    f'<span class="badge badge-{chimera_status[0]} rounded-pill d-inline" data-mdb-toggle="tooltip" rel="tooltip" title="{chimera_status[1]}">' \
                                        f'{chimera_status[2]}' \
                                    f'</span>' \
                                f'</td>'\
                                f'<td>' \
                                    f'<span class="badge badge-info rounded-pill d-inline">' \
                                        f'{account_proxy}' \
                                    f'</span>'\
                                f'</td>'\
                                f'<td>' \
                                    f'<span data-mdb-toggle="tooltip" rel="tooltip"title="Возраст взят из .json файла">' \
                                        f'{register_time_in_days}' \
                                    f'</span>' \
                                f'</td>'\
                                f'<td>' \
                                    f'<button id="{session_name}" onclick=getSmsCode("{session_name}") class="btn btn-info btn-sm btn-rounded" data-mdb-toggle="tooltip" rel="tooltip" title="Получить смс" type="button"><i class="fa-solid fa-phone-volume"></i></button>&nbsp;'\
                                f'</td>'\
                           f'</tr>'
            accounts_html += account_item
    except Exception as Ass:
        print(Ass)


    if len(accounts_html) == 0:
        accounts_html = '<td class="text-center" colspan="7">Для начала работы поместите аккаунты в папку accounts/input</td>'

    async_eel.renderAccountsList(accounts_html)
    if render_message is None:
        async_eel.displayToast(f'Список аккаунтов обновлён!<br/>Найдено сессий: {len(sessions)} ', 'success')
    else:
        async_eel.displayToast(f'{render_message[0]}', render_message[1])
    async_eel.updateAccountsBadges(accounts_all, accounts_valid, accounts_not_checked, accounts_spam_block)



@async_eel.expose
async def copy_accounts(dir_path:str)->int:
    #by dir path copy to input dir by software with extension session and json
    try:
        base_dir = os.getcwd()
        main_dir_path = rf"{base_dir}/accounts/input/"
        files = [shutil.copy2(filepath.absolute(), f"{main_dir_path}{filepath.name}") for filepath in
                 chain(pathlib.Path(dir_path).glob('*.session'), pathlib.Path(dir_path).glob('*.json'))]
        return int(len(files) / 2) if len(files) > 0 else len(files)
    except Exception as e:
        print(e)