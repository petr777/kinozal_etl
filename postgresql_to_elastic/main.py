from typing import List, Generator
from state import JsonFileStorage, State
from datetime import datetime, timezone
from extractors.movies import PostgresMovies
from transforms.movies import Transformation
from loaders.movies import ElasticMovies
from model import Person, Movies
from enum import Enum
from utility.backoff import backoff
from loguru import logger
from settings import pg_dsl, es_dsl, LocalStorage, batch_limit, initial_state
import time


class Role(Enum):
    ACTOR = 'actor'
    WRITER = 'writer'
    DIRECTOR = 'director'

    @staticmethod
    def list():
        return list(map(lambda r: r.value, Role))


def transform(batch_data: List[dict]) -> List[Movies]:
    trans = Transformation()
    good_data = []
    for _id, data in trans.groupby(batch_data, 'fw_id'):
        movie = dict()
        movie['id'] = _id
        movie['title'] = trans.uniq_by_key(data, 'title')[0]
        movie['description'] = trans.uniq_by_key(data, 'description')[0]
        movie['rating'] = trans.uniq_by_key(data, 'rating')[0]
        movie['genre'] = trans.uniq_by_key(data, 'name')

        for role in Role.list():
            role_data = [
                Person(**item)
                for item in trans.fetch_by_filter(data, 'role', role, 'id')
            ]
            movie[f'{role}'] = role_data
            movie[f'{role}s_names'] = [person.name for person in role_data]
        mv = Movies(**movie)
        good_data.append(mv)
    return good_data


def extract(pg_db, state, table_name: str) -> Generator:

    def clean_arr_ids(ids):
        return [_id[0] for _id in ids]

    if not state.get_state(table_name):
        state.set_state(table_name, initial_state.isoformat())

    curremt_state = datetime.fromisoformat(state.get_state(table_name))

    modified_ids = pg_db.get_all_ids_gte_modified(
        table_name=table_name,
        state_date=curremt_state,
        limit=batch_limit
    )

    for batch_ids in modified_ids:

        if table_name == 'person':
            batch_ids = pg_db.get_person_data(
                clean_arr_ids(batch_ids)
            )
        if table_name == 'genre':
            batch_ids = pg_db.get_genre_data(
                clean_arr_ids(batch_ids)
            )

        data = pg_db.get_data_from_elastic_movies(clean_arr_ids(batch_ids))
        yield data


def load(es_db, data: List[Movies]):
    es_db.save_bulk('movies', data)


@backoff(logger=logger)
def run():
    for table_name in ('film_work', 'genre', 'person'):
        storage = JsonFileStorage(LocalStorage)
        state = State(storage)
        with PostgresMovies(pg_dsl) as pg_db, ElasticMovies(es_dsl) as es_db:
            logger.info(f'Синхронизуруем таблицу {table_name}')
            for batch_data in extract(pg_db, state, table_name):
                good_data = transform(batch_data)
                load(es_db, good_data)
                state.set_state(
                    table_name, datetime.now(timezone.utc).isoformat())


if __name__ == '__main__':
    while True:
        run()
        time.sleep(5)
