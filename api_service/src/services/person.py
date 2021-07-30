from functools import lru_cache
from http import HTTPStatus

from aioredis import Redis
from elasticsearch import AsyncElasticsearch
from fastapi import Depends, HTTPException

from db.elastic import get_elastic
from db.redis import get_redis
from models.person import Person
from services.base import MultiMatchSearchMixin, Service


class PersonService(MultiMatchSearchMixin, Service):
    es_index = "persons"
    model_type = Person

    async def search_persons(
        self, url: str, query: str, page_number: int, page_size: int
    ) -> list[Person]:

        return await self._multi_match_search(
            url, query, page_number, page_size, ["first_name", "last_name"]
        )



@lru_cache()
def get_person_service(
    redis: Redis = Depends(get_redis),
    elastic: AsyncElasticsearch = Depends(get_elastic),
) -> PersonService:
    return PersonService(redis, elastic)
