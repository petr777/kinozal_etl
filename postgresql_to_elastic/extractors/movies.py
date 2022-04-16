import datetime
from db.pg_db import PostgresBase
from typing import List
from psycopg2.extras import DictRow


class PostgresMovies(PostgresBase):

    def clean_arr_ids(self, ids) -> List[str]:
        return [_id[0] for _id in ids]

    def get_ids_gte_modified(
            self,
            table_name: str,
            state_date: datetime,
            skip: int = 0,
            limit: int = 100):
        sql = f"""
        SELECT id FROM {table_name}
        WHERE modified >= '{state_date}'
        ORDER BY modified
        LIMIT {limit} OFFSET {skip};"""
        return self.query(sql).fetchall()

    def get_all_ids_gte_modified(
            self,
            table_name: str,
            state_date: datetime,
            limit: int = 100) -> List[DictRow]:
        skip = 0
        while True:
            data = self.get_ids_gte_modified(
                table_name=table_name,
                state_date=state_date,
                skip=skip,
                limit=limit,
            )
            if not data:
                break
            yield data
            skip += limit

    def get_person_data(self, ids: List[str]) -> List[DictRow]:
        sql = """
            SELECT fw.id
            FROM content.film_work fw
            LEFT JOIN content.person_film_work pfw ON pfw.film_work_id = fw.id
            WHERE pfw.person_id IN %(ids)s
            ORDER BY fw.modified
        """
        sql = self.cursor.mogrify(sql, {'ids': tuple(ids)})
        return self.query(sql).fetchall()

    def get_genre_data(self, ids: List[str]) -> List[DictRow]:
        sql = """
            SELECT fw.id
            FROM content.film_work fw
            LEFT JOIN content.genre_film_work gfw ON gfw.film_work_id = fw.id
            WHERE gfw.genre_id IN %(ids)s
            ORDER BY fw.modified
        """
        sql = self.cursor.mogrify(sql, {'ids': tuple(ids)})
        return self.query(sql).fetchall()

    def get_data_from_elastic_movies(self, film_work_ids) -> List[DictRow]:
        sql = """SELECT
            fw.id as fw_id,
            fw.title,
            fw.description,
            fw.rating,
            fw.type,
            fw.created,
            fw.modified,
            pfw.role,
            pfw.id as pfw_id,
            p.id,
            p.full_name,
            g.name
        FROM content.film_work fw
        LEFT JOIN content.person_film_work pfw ON pfw.film_work_id = fw.id
        LEFT JOIN content.person p ON p.id = pfw.person_id
        LEFT JOIN content.genre_film_work gfw ON gfw.film_work_id = fw.id
        LEFT JOIN content.genre g ON g.id = gfw.genre_id
        WHERE fw.id IN %(film_work_ids)s;
        """
        sql = self.cursor.mogrify(sql, {'film_work_ids': tuple(film_work_ids)})
        return self.query(sql).fetchall()

    def first_modified(self, table_name: str) -> DictRow:
        sql = f"""SELECT modified FROM {table_name} ORDER BY modified;"""
        return self.query(sql).fetchone()
