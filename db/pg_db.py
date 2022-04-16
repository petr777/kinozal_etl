import psycopg2
from psycopg2.extras import DictCursor
from utility.backoff import backoff
from loguru import logger


class PostgresBase:

    def __init__(self, dsl):
        self.dsl = dsl

    @backoff(logger=logger)
    def __enter__(self):
        self.connection = psycopg2.connect(
            **self.dsl, cursor_factory=DictCursor
        )
        self.cursor = self.connection.cursor()
        return self

    def query(self, sql):
        try:
            self.cursor.execute(sql, [])
        except (psycopg2.OperationalError, psycopg2.InterfaceError):
            self.__enter__()

        return self.cursor

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.connection.commit()
        self.connection.close()