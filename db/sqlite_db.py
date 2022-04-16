from pathlib import Path
import sqlite3


class SQLiteBase:

    def __init__(self, path: Path):
        self.path = path

    def dict_factory(self, cursor, row):
        d = {}
        for idx, col in enumerate(cursor.description):
            d[col[0]] = row[idx]
        return d

    def __enter__(self):
        self.connection: sqlite3.Connection = sqlite3.connect(self.path)
        self.connection.row_factory = self.dict_factory
        self.cursor: sqlite3.Cursor = self.connection.cursor()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.connection.close()