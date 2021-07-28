from functools import lru_cache

from aioredis import Redis
from elasticsearch import AsyncElasticsearch
from fastapi import Depends

from db.elastic import get_elastic
from db.redis import get_redis
from models.genre import Genre
from services.base import Service


class GenreService(Service):
    es_index = "genres"
    model_type = Genre

    async def genre_list(self, url: str) -> list[Genre]:
        return await self._search(url, {"query": {"match_all": {}}})


@lru_cache()
def get_genre_service(
    redis: Redis = Depends(get_redis),
    elastic: AsyncElasticsearch = Depends(get_elastic),
) -> GenreService:
    return GenreService(redis, elastic)
