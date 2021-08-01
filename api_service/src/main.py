import logging
from datetime import timedelta

import aioredis
import uvicorn
from elasticsearch import AsyncElasticsearch
from fastapi import FastAPI, Request, Response
from fastapi.responses import ORJSONResponse
from httpx import AsyncClient, RequestError
from aiobreaker import CircuitBreaker, CircuitBreakerListener

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

auth_breaker = CircuitBreaker(fail_max=5)


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    headers = request.headers
    base_url = "http://" + config.AUTH_URL
    try:
        auth_answer = await send_circuit_request(f"{base_url}/auth/v1/authorize", headers=dict(headers))
    except RequestError:
        return Response(content="Anonymous user", status_code=401)  # будем возвращать фильмы для анонимных юзеров
    if auth_answer.status_code == 200:
        data = auth_answer.json()
        if data["roles"]:  # здесь должна быть проверка роли, если просто юзер, то одни данные, если подписчик - другие
            response = await call_next(request)
            return response
        return Response(content="Not allowed", status_code=403)
    return Response(content="Anonymous user", status_code=401)  # будем возвращать фильмы для анонимных юзеров


class LogListener(CircuitBreakerListener):
    def state_change(self, breaker, old, new):
        logging.info(f"{old.state} -> {new.state}")


@auth_breaker
async def send_circuit_request(url: str, headers: dict):
    async with AsyncClient() as client:
        answer = await client.get(url, headers=headers)
        logging.info(answer)
        return answer


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        log_config=LOGGING,
        log_level=logging.DEBUG,
        reload=True,
    )
