import glob
import json
import os
import zipfile
from os.path import exists, basename

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

        for session in sessions:
            if session:
                if not exists(session.replace('session', 'json')):
                    os.remove(session)
                    sessions.remove(session)

        accounts_html = ''

        accounts_all = 0
        accounts_valid = 0
        accounts_not_checked = 0
        accounts_spam_block = 0
        accounts_deleted = 0

        for session_path in sessions:
            account_front_status_filter = None
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
                account_created_at = datetime.utcfromtimestamp(int(account_json_config[1]['register_time'])).strftime(
                    '%d-%m-%Y')

                current_d = datetime.strptime(current_date, "%d-%m-%Y")
                reg_d = datetime.strptime(account_created_at, "%d-%m-%Y")
                register_time_in_days = f'{current_d - reg_d}'.split(' ')[0]
                if register_time_in_days == '0:00:00':
                    register_time_in_days = 'Добавлен сегодня'

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
                    accounts_deleted += 1
                    chimera_status = ['dark', 'Аккаунт удалён', 'Удалён']
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
                chimera_status = ['danger', 'Ошибка чтения аккаунта', 'Ошибка']
                user_fl_names = 'Неизвестно'
                register_time_in_days = 'NaN дней'
            print(account_front_status_filter)
            accounts_all += 1
            session_name = os.path.basename(os.path.normpath(session_path))
            account_item = f'<tr id="tr_{session_name}">' \
                               f'<td>' \
                               f'<div class="form-check">' \
                               f'<input class="form-check-input" type="checkbox" {"checked" if session_name in accounts_names else ""} value="{session_name}" data-account-status="{chimera_status[2]}"/>' \
                               f'</div>' \
                               f'</td>' \
                               f'<td>' \
                               f'<div class="d-flex align-items-center">' \
                               f'<img alt="" class="rounded-circle account-picture" src="{account_picture}"></>' \
                               f'<div class="ms-3">' \
                               f'<p class="fw-bold mb-1 overflow-hidden-p">{user_fl_names}</p>' \
                               f'<p class="text-muted mb-0 overflow-hidden-p">@{username}</p>' \
                               f'</div>' \
                               f'</div>' \
                               f'</td>' \
                               f'<td>' \
                               f'<p class="fw-normal mb-1">{phone_number}</p>' \
                               f'<p class="text-muted mb-0">{readable_gender}</p>' \
                               f'</td>' \
                               f'<td>' \
                               f'<span class="badge badge-{chimera_status[0]} rounded-pill d-inline" data-mdb-toggle="tooltip" rel="tooltip" title="{chimera_status[1]}">' \
                               f'{chimera_status[2]}' \
                               f'</span>' \
                               f'</td>' \
                               f'<td>' \
                               f'<span class="badge badge-info rounded-pill d-inline">' \
                               f'{account_proxy}' \
                               f'</span>' \
                               f'</td>' \
                               f'<td>' \
                               f'<span data-mdb-toggle="tooltip" rel="tooltip"title="Возраст взят из .json файла">' \
                               f'{register_time_in_days}' \
                               f'</span>' \
                               f'</td>' \
                               f'<td>' \
                               f'<button id="{session_name}" onclick=getSmsCode("{session_name}") class="btn btn-info btn-sm btn-rounded" data-mdb-toggle="tooltip" rel="tooltip" title="Получить смс" type="button"><i class="fa-solid fa-phone-volume"></i></button>&nbsp;' \
                               f'</td>' \
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
    async_eel.updateAccountsBadges(accounts_all, accounts_valid, accounts_not_checked, accounts_spam_block,
                                   accounts_deleted)


@async_eel.expose
async def copy_accounts(dir_path: str) -> int:
    # by dir path copy to input dir by software with extension session and json
    try:
        base_dir = os.getcwd()
        main_dir_path = rf"{base_dir}/accounts/input/"
        files = [shutil.copy2(filepath.absolute(), f"{main_dir_path}{filepath.name}") for filepath in
                 chain(pathlib.Path(dir_path).glob('*.session'), pathlib.Path(dir_path).glob('*.json'))]
        return int(len(files) / 2) if len(files) > 0 else len(files)
    except Exception as e:
        print(e)

@async_eel.expose
async def delete_accounts(accounts: list):
    try:
        base_dir = os.getcwd()
        main_dir_path = rf"{base_dir}/accounts/input/"
        account_remove_counter = 0
        for account in accounts:
            account_json_path = f"{main_dir_path}{account.replace('session','json')}"
            account_session_path = f"{main_dir_path}{account}"
            try:
                os.remove(account_json_path)
                account_remove_counter = account_remove_counter + 1
            except:
                pass
            try:
                os.remove(account_session_path)
            except:
                pass
        async_eel.displayToast(f'Аккаунтов удалено: {account_remove_counter} ', 'success')
        await render_accounts_list()
    except Exception as e:
        await render_accounts_list()
        print(e)


@async_eel.expose
async def create_zip(accounts: list):
    try:
        now = datetime.now()
        file_zip_name = f'{now.strftime("%d_%m_%Y_%H_%M_%S")}_archive.zip'
        desktop =pathlib.Path.home() / 'Desktop'
        archive_path = f"{desktop}/{file_zip_name}"
        zip_achive = zipfile.ZipFile(archive_path, 'w')
        base_dir = os.getcwd()
        main_dir_path = rf"{base_dir}/accounts/input/"
        for account in accounts:
            account_json_path = os.path.join(main_dir_path,account.replace('session','json'))
            account_session_path = os.path.join(main_dir_path,account)
            zip_achive.write(account_session_path, basename(account_session_path))
            zip_achive.write(account_json_path,basename(account_json_path))
        zip_achive.close()
        async_eel.displayToast(f'Архив {file_zip_name} с {len(accounts)} аккаунтами создан на рабочем столе. ', 'success')
    except Exception as e:
        print(e)



@async_eel.expose
async def render_accounts_by_filter(search_filter = None):
    try:
        input_sessions_folder = 'accounts/input/'
        sessions = [f for f in glob.glob(f"{input_sessions_folder}*.session")]

        for session in sessions:
            if session:
                if not exists(session.replace('session', 'json')):
                    os.remove(session)
                    sessions.remove(session)

        accounts_html = ''

        accounts_all = 0
        accounts_valid = 0
        accounts_not_checked = 0
        accounts_spam_block = 0
        accounts_deleted = 0

        for session_path in sessions:
            account_front_status_filter = None
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
                account_created_at = datetime.utcfromtimestamp(int(account_json_config[1]['register_time'])).strftime(
                    '%d-%m-%Y')

                current_d = datetime.strptime(current_date, "%d-%m-%Y")
                reg_d = datetime.strptime(account_created_at, "%d-%m-%Y")
                register_time_in_days = f'{current_d - reg_d}'.split(' ')[0]
                if register_time_in_days == '0:00:00':
                    register_time_in_days = 'Добавлен сегодня'

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
                    accounts_deleted += 1
                    chimera_status = ['dark', 'Аккаунт удалён', 'Удалён']
                else:
                    chimera_status = ['default', 'Не удалось распознать', 'Неизвестно']
                account_front_status_filter = chimera_status

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
                chimera_status = ['danger', 'Ошибка чтения аккаунта', 'Ошибка']
                user_fl_names = 'Неизвестно'
                register_time_in_days = 'NaN дней'
            if account_front_status_filter[2] == search_filter or search_filter is None:
                accounts_all += 1
                session_name = os.path.basename(os.path.normpath(session_path))
                account_item = f'<tr id="tr_{session_name}">' \
                               f'<td>' \
                               f'<div class="form-check">' \
                               f'<input class="form-check-input" type="checkbox"  value="{session_name}" data-account-status="{chimera_status[2]}"/>' \
                               f'</div>' \
                               f'</td>' \
                               f'<td>' \
                               f'<div class="d-flex align-items-center">' \
                               f'<img alt="" class="rounded-circle account-picture" src="{account_picture}"></>' \
                               f'<div class="ms-3">' \
                               f'<p class="fw-bold mb-1 overflow-hidden-p">{user_fl_names}</p>' \
                               f'<p class="text-muted mb-0 overflow-hidden-p">@{username}</p>' \
                               f'</div>' \
                               f'</div>' \
                               f'</td>' \
                               f'<td>' \
                               f'<p class="fw-normal mb-1">{phone_number}</p>' \
                               f'<p class="text-muted mb-0">{readable_gender}</p>' \
                               f'</td>' \
                               f'<td>' \
                               f'<span class="badge badge-{chimera_status[0]} rounded-pill d-inline" data-mdb-toggle="tooltip" rel="tooltip" title="{chimera_status[1]}">' \
                               f'{chimera_status[2]}' \
                               f'</span>' \
                               f'</td>' \
                               f'<td>' \
                               f'<span class="badge badge-info rounded-pill d-inline">' \
                               f'{account_proxy}' \
                               f'</span>' \
                               f'</td>' \
                               f'<td>' \
                               f'<span data-mdb-toggle="tooltip" rel="tooltip"title="Возраст взят из .json файла">' \
                               f'{register_time_in_days}' \
                               f'</span>' \
                               f'</td>' \
                               f'<td>' \
                               f'<button id="{session_name}" onclick=getSmsCode("{session_name}") class="btn btn-info btn-sm btn-rounded" data-mdb-toggle="tooltip" rel="tooltip" title="Получить смс" type="button"><i class="fa-solid fa-phone-volume"></i></button>&nbsp;' \
                               f'</td>' \
                               f'</tr>'
                accounts_html += account_item
    except Exception as Ass:
        print(Ass)

    if len(accounts_html) == 0:
        accounts_html = '<td class="text-center" colspan="7">Для начала работы поместите аккаунты в папку accounts/input</td>'

    async_eel.renderAccountsList(accounts_html)