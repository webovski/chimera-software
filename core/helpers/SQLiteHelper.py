import sqlite3


def get_connection():
    try:
        sqliteConnection = sqlite3.connect('temp-parsing.db', check_same_thread=False)
        sqlite_create_table_query = '''CREATE TABLE if not exists parsed_users (
                                    user_id INTEGER PRIMARY KEY,
                                    full_name TEXT NULL,
                                    username TEXT NULL,
                                    has_avatar INTEGER NULL,
                                    was_online TEXT NULL,
                                    phone INTEGER NULL,
                                    is_admin INTEGER NULL,
                                    has_premium INTEGER NULL,
                                    is_scam INTEGER NULL
                                    );'''

        cursor = sqliteConnection.cursor()
        cursor.execute(sqlite_create_table_query)
        sqliteConnection.commit()

        return sqliteConnection

    except sqlite3.Error as error:
        print("Error while creating a temp sqlite table", error)


async def insert_parser_user(
        connection,
        user_id: int,
        full_name: str,
        username: str,
        has_avatar: int,
        was_online: str,
        phone: int,
        is_admin: int,
        is_premium: int,
        is_scam: int
):
    try:
        connection.cursor().execute(
            "INSERT INTO parsed_users (user_id, full_name, username, has_avatar, was_online, phone, is_admin, has_premium, is_scam) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (user_id, full_name, username, has_avatar, was_online, phone, is_admin, is_premium, is_scam))
        connection.commit()
    except Exception as Error:
        pass


def close_connection(connection):
    connection.close()
