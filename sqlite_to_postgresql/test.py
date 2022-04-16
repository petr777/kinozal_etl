from settings import PG_DB, SQLLITE_DB
from load_data import SQLite, Postgres, get_model


def check_data(sqlite_db, pg_db, table_name, limit: int = 1000):
    model = get_model(table_name)
    skip = 0
    while True:
        sqlite_rows = sqlite_db.get_many(table_name, skip=skip, limit=limit)
        pg_rows = pg_db.get_many(table_name, skip=skip, limit=limit)

        if not sqlite_rows and not pg_rows:
            break

        sqlite_data = [model(**row) for row in sqlite_rows]
        pg_data = [model(**row) for row in pg_rows]

        if sqlite_data != pg_data:
            return False
        skip += limit
    return True


def check_count(sqlite_db, pg_db, table_name):
    return sqlite_db.count_data(table_name) == pg_db.count_data(table_name)


def check(sqlite_db, pg_db):
    tables = [
        'genre', 'genre_film_work',
        'person_film_work', 'person', 'film_work'
        ]
    for name in tables:
        assert check_count(
            sqlite_db, pg_db, name
        ), f'Разное кол-во записей в таблице {name}'

        assert check_data(
            sqlite_db, pg_db, name
        ), f'В таблице {name} записи не идентичны'


if __name__ == "__main__":
    with SQLite(SQLLITE_DB) as sqlite_db, Postgres(PG_DB) as pg_db:
        check(sqlite_db, pg_db)
