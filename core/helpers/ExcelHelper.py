from datetime import datetime

import xlsxwriter as xlsxwriter


def create_excel_doc(users_query: list[dict]):
    """generate excel report from query set users"""
    try:
        now = datetime.now()
        file_name = f"{now.strftime('%d_%m_%Y %H_%M_%S')}.xlsx"
        workbook = xlsxwriter.Workbook(file_name)
        cell_format = workbook.add_format()
        cell_format_text = workbook.add_format()
        cell_format_text.set_align('center')
        cell_format.set_align('center')
        worksheet = workbook.add_worksheet()
        worksheet.write('A1', 'Идентификатор', cell_format)
        worksheet.write('B1', 'Имя', cell_format)
        worksheet.write('C1', 'Никнейм', cell_format)
        worksheet.write('D1', 'Телефон', cell_format_text)
        worksheet.write('E1', 'Посещаемость', cell_format)
        worksheet.write('F1', 'Премиум', cell_format)
        worksheet.write('G1', 'Статус', cell_format)
        worksheet.write('H1', 'Наличие фото', cell_format)
        worksheet.write('I1', 'Скам', cell_format)
        worksheet.write('J1', 'Бот', cell_format)

        worksheet.set_column(0, 11, 22)
        index = 2
        for user in users_query:
            try:
                user_id = user['user_id']
                full_name = user['full_name']
                username = user['username']
                has_avatar = '+' if user['has_avatar'] == 1 else '-'
                online_status = user['was_online']
                phone = user['phone'] if user['phone'] else ''
                # is_admin or not
                user_role = 'Администратор' if user['is_admin'] == 1 else 'Участник'
                is_scammer = '+' if user['is_scam'] == 1 else '-'
                premium = '+' if user['has_premium'] == 1 else '-'
                is_bot = '+' if user['is_bot'] == 1 else '-'

                worksheet.write(f'A{index}', user_id, cell_format_text)
                worksheet.write(f'B{index}', full_name, cell_format_text)
                worksheet.write(f'C{index}', username, cell_format_text)
                worksheet.write(f'D{index}', phone, cell_format_text)
                worksheet.write(f'E{index}', online_status, cell_format_text)
                worksheet.write(f'F{index}', premium, cell_format_text)
                worksheet.write(f'G{index}', user_role, cell_format_text)
                worksheet.write(f'H{index}', has_avatar, cell_format_text)
                worksheet.write(f'I{index}', is_scammer, cell_format_text)
                worksheet.write(f'J{index}', is_bot, cell_format_text)

            except Exception as UnexpectedWriteRowError:
                print(f'Generat row report error {UnexpectedWriteRowError}')
                pass

            index += 1
        workbook.close()
        return file_name
    except Exception as UnexpectedWriteExcelError:
        print(f'Excel generate report error: {UnexpectedWriteExcelError}')
        return UnexpectedWriteExcelError
