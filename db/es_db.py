from elasticsearch import Elasticsearch
from utility.backoff import backoff
from loguru import logger


class ElasticBase:

    def __init__(self, dsl):
        self.dsl = dsl

    @backoff(logger=logger)
    def __enter__(self):
        self.client = Elasticsearch(**self.dsl)
        if not self.client.ping():
            raise ValueError("Elasticsearch connection error")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.client.close()
