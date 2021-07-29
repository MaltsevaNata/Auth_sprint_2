import logging
import os

import requests

import aioredis
import uvicorn
from elasticsearch import AsyncElasticsearch
from fastapi import FastAPI, Request, Response
from fastapi.responses import ORJSONResponse

from api.v1 import filmwork, genre, person
from core import config
from core.logger import LOGGING
from db import elastic, redis

app = FastAPI(
    title=config.PROJECT_NAME,
    docs_url="/api/openapi",
    openapi_url="/api/openapi.json",
    default_response_class=ORJSONResponse,
)


@app.on_event("startup")
async def startup():
    redis.redis = await aioredis.create_redis_pool(
        (config.REDIS_HOST, config.REDIS_PORT), minsize=10, maxsize=20
    )
    elastic.es = AsyncElasticsearch(
        hosts=[f"{config.ELASTIC_HOST}:{config.ELASTIC_PORT}"]
    )


@app.on_event("shutdown")
async def shutdown():
    await redis.redis.close()
    await elastic.es.close()


app.include_router(filmwork.router, prefix="/api/v1/film", tags=["film"])
app.include_router(genre.router, prefix="/api/v1/genre", tags=["genre"])
app.include_router(person.router, prefix="/api/v1/person", tags=["person"])


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    headers = request.headers
    if not "authorization" in headers:
        # здесь нужно возвращать ответ для анонимного пользователя
        return Response(content="Anonymous user", status_code=401)
    base_url = "http://" + config.AUTH_URL
    auth_answer = requests.get(url=f"{base_url}/auth/v1/authorize", headers=headers)
    if auth_answer.status_code == 200:
        data = auth_answer.json()
        if data["roles"]:  # здесь должна быть проверка роли, если просто юзер, то одни данные, если подписчик - другие
            response = await call_next(request)
            return response
        return Response(content="Not allowed", status_code=403)
    return Response(content="Anonymous user", status_code=401)


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        log_config=LOGGING,
        log_level=logging.DEBUG,
        reload=True,
    )
