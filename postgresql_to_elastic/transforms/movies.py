import operator
from enum import Enum
from itertools import groupby
from typing import List, Dict, Generator


class Role(Enum):
    ACTOR = 'actor'
    WRITER = 'writer'
    DIRECTOR = 'director'

    @staticmethod
    def list():
        return list(map(lambda r: r.value, Role))


class Transformation:

    def groupby(self, data: List[Dict], _id: str) -> Generator:
        data = sorted(data, key=operator.itemgetter(_id))
        for _id, new_data in groupby(data, key=operator.itemgetter(_id)):
            yield _id, list(new_data)

    def fetch_by_filter(
            self, data: List[Dict],
            field: str,
            key: str,
            filter: str) -> List:

        result = [item for item in data if item[field] == key]
        result = list({v[filter]: v for v in result}.values())
        return result

    def uniq_by_key(self, data: List[Dict], filter: str) -> List:
        result = list({v[filter]: v for v in data}.values())
        return [item[filter] for item in result]
