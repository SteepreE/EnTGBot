import sqlite3


MESSAGES_LIMIT = 5


class Database:

    def __init__(self, path: str, table_name: str):
        self._path = path
        self._table_name = table_name
        self._create_table()

    def _get_connection(self):
        return sqlite3.connect(self._path)

    def _create_table(self):
        conn = self._get_connection()
        cur = conn.cursor()

        cur.execute(f'''CREATE TABLE IF NOT EXISTS {self._table_name} 
                        (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER,
                        message_type TEXT, data_id TEXT, caption TEXT)''')

        conn.commit()
        conn.close()

    def add_new_message(self, message_type: str, data_id: str, caption: str, user_id: int):
        conn = self._get_connection()
        cur = conn.cursor()

        cur.execute(f'''INSERT INTO {self._table_name} 
                    (user_id, message_type, data_id, caption)
                    VALUES (?,?,?,?)''',
                    (user_id, message_type, data_id, caption))

        conn.commit()
        conn.close()

    def clear_table(self):
        conn = self._get_connection()
        cur = conn.cursor()

        cur.execute(f'DELETE * FROM {self._table_name}')

        conn.commit()
        conn.close()

    def get_all_items(self):
        conn = self._get_connection()
        cur = conn.cursor()

        cur.execute(f'SELECT * FROM {self._table_name}')
        items = cur.fetchall()

        conn.commit()
        conn.close()

        return items

    def get_orders_by_offset(self, offset):
        conn = self._get_connection()
        cur = conn.cursor()

        cur.execute(f'SELECT * FROM {self._table_name} ORDER BY id DESC LIMIT {MESSAGES_LIMIT} OFFSET {offset * MESSAGES_LIMIT}')
        result = cur.fetchall()

        conn.close()

        return result

    def get_last_added_item(self):
        conn = self._get_connection()
        cur = conn.cursor()

        cur.execute(f'SELECT * FROM {self._table_name} ORDER BY id DESC LIMIT 1')
        item = cur.fetchone()

        conn.commit()
        conn.close()

        return item
