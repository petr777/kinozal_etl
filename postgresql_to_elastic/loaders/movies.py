from elasticsearch import helpers
from typing import List, Generator
from db.es_db import ElasticBase
from loguru import logger


class ElasticMovies(ElasticBase):

    def generate_elastic_data(self, index, data: list) -> Generator:
        for item in data:
            yield {
                '_index': index,
                '_id': str(item.id),
                **item.dict(),
                'director': [p.name for p in item.director],

            }

    def save_bulk(self, index, data: List[dict]) -> None:
        res, _ = helpers.bulk(
            self.client,
            self.generate_elastic_data(index, data)
        )
        logger.info(f'Синхронизированно записей {res}')
