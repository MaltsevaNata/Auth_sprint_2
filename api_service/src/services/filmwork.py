from functools import lru_cache
from typing import Optional
from http import HTTPStatus

from aioredis import Redis
from elasticsearch import AsyncElasticsearch
from fastapi import Depends, HTTPException

from db.elastic import get_elastic
from db.redis import get_redis
from models.filmwork import FilmWork
from .base import MultiMatchSearchMixin, Service


class FilmService(MultiMatchSearchMixin, Service):
    es_index = "movies"
    model_type = FilmWork

    async def get_films(
        self,
        url,
        page_number: int,
        page_size: int,
        sort: str,
        genre: Optional[str] = None,
    ) -> list[FilmWork]:
        query = {"match_all": {}}

        if genre:
            query = {"match": {"genres.name": genre}}

        body = {
            "from": page_number * page_size,
            "size": page_size,
            "query": query,
            "sort": {"imdb_rating": "asc" if sort == "imdb_rating" else "desc"},
        }

        return await self._search(url, body=body)

    async def search_films(
        self, url: str, query: str, page_number: int, page_size: int
    ) -> list[FilmWork]:

        return await self._multi_match_search(
            url, query, page_number, page_size, ["title", "description"]
        )


@lru_cache()
def get_film_service(
    redis: Redis = Depends(get_redis),
    elastic: AsyncElasticsearch = Depends(get_elastic),
) -> FilmService:
    return FilmService(redis, elastic)
