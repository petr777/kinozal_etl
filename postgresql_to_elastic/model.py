from typing import Optional, List
from pydantic import BaseModel
from pydantic.fields import Field


class Person(BaseModel):
    id: str
    name: str = Field(alias='full_name')


class Movies(BaseModel):
    id: str
    imdb_rating: Optional[float] = Field(alias='rating', default=0.0)
    genre: Optional[List[str]] = []
    title: str
    description: Optional[str] = None
    director: List[Person] = Field(alias='director', default=[])
    actors: List[Person] = Field(alias='actor', default=[])
    actors_names: List = []
    writers: List[Person] = Field(alias='writer', default=[])
    writers_names: List = []
