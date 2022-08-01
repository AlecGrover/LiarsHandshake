import sqlite3
from datetime import datetime

LOCATION = "data"
PLAYERS_TABLE = "players"


class PlayerDB:

    def __init__(self, instance_number):
        self.instance_number = instance_number
        self.db = sqlite3.connect(LOCATION)
        self.cursor = self.db.cursor()

        _sql = f"""CREATE TABLE IF NOT EXISTS {PLAYERS_TABLE} (uuid text PRIMARY KEY, account_data text, most_recent_activity text)""";
        self.cursor.execute(_sql)
        self.db.commit()

        self.cursor.execute("PRAGMA database_list")
        self.db_list = self.cursor.fetchall()

    def set_player_data(self, _uuid, _data):
        _sql = f"""INSERT INTO {PLAYERS_TABLE}(uuid, account_data, most_recent_activity) VALUES 
        (?, ?, JULIANDAY('now'))
            ON CONFLICT (uuid) DO UPDATE SET 
            account_data = excluded.account_data, most_recent_activity = excluded.most_recent_activity;"""
        self.cursor.execute(_sql, (_uuid, _data))
        self.db.commit()

    def get_player_data(self, _uuid):
        _sql = f"""SELECT account_data FROM {PLAYERS_TABLE} WHERE uuid = ?"""
        self.cursor.execute(_sql, (_uuid, ))
        data = self.cursor.fetchall()
        if len(data) > 0:
            return data[0][0]
        else:
            return None

    def get_db_list(self):
        return self.db_list;

    def clear_inactive_users(self, timeout_days):
        _sql = f"""DELETE FROM {PLAYERS_TABLE}
        WHERE (JULIANDAY('now', '-{timeout_days} days') > most_recent_activity)"""
        self.cursor.execute(_sql)
        self.db.commit()

    def shutdown(self):
        self.db.close()
