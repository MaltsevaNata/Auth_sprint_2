import logging
from typing import AnyStr, Callable, Optional

import elasticsearch
import orjson
from aioredis import Redis
from elasticsearch import AsyncElasticsearch
from pydantic import BaseModel

RESPONSE_CACHE_EXPIRE_IN_SECONDS = 60 * 5  # 5 минут


class Service:
    # Название инедкса в Elasticsearch который использует конкретный сервис.
    # Должен быть переопределен в подклассах.
    es_index = ""

    # Тип модели используемый для формирования ответа.
    # Должен быть переопределен в подклассах.
    model_type = BaseModel

    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        self.redis = redis
        self.elastic = elastic

    async def _get_from_cache(self, url: str) -> Optional[AnyStr]:
        if response := await self.redis.get(url):
            logging.info("Got from cache %r", url)
            return response

    async def _put_to_cache(self, url: str, obj) -> None:
        logging.info("Put to cache %r", url)
        await self.redis.set(
            url, orjson.dumps(obj), expire=RESPONSE_CACHE_EXPIRE_IN_SECONDS
        )

    async def _get_from_cache_or_elastic(self, url: str, es_method: Callable, **kwargs):
        """
        Выполняет запрос к Elasticsearch если заданный url отсутствует в кэше,
        иначе возваращает результат из кэша.

        :param url: строка запроса.
        :param es_method: метод elasticsearch который будет вызван для
            получения результата, если url не найден в кэше.
        :param kwargs: параметры которые будут переданы в es_method.
        """
        if response := await self._get_from_cache(url):
            return orjson.loads(response)

        response = await es_method(**kwargs)

        await self._put_to_cache(url, response)

        return response

    async def get_by_id(self, url: str, id: str):
        try:
            doc = await self._get_from_cache_or_elastic(
                url, self.elastic.get, index=self.es_index, id=id
            )
            return self.model_type(**doc["_source"])
        except elasticsearch.NotFoundError:
            return None

    async def _search(self, url: str, body: dict):
        response = await self._get_from_cache_or_elastic(
            url, self.elastic.search, index=self.es_index, body=body
        )
        return [self.model_type(**doc["_source"]) for doc in response["hits"]["hits"]]


class MultiMatchSearchMixin:
    """
    Примесь для полнотекстового поиска по нескольким полям.
    """

    async def _multi_match_search(
        self, url: str, query: str, page_number: int, page_size: int, fields: list[str]
    ):
        query = {"multi_match": {"query": query, "fields": fields}}

        body = {
            "from": page_number * page_size,
            "size": page_size,
            "query": query,
        }

        return await self._search(url, body)
