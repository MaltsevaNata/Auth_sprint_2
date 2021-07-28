from pydantic import BaseSettings, Field


class TestSettings(BaseSettings):
    es_host: str = Field("http://127.0.0.1", env="ELASTIC_HOST")
    es_port: str = Field("9200", env="ELASTIC_PORT")
    redis_host: str = Field("127.0.0.1", env="REDIS_HOST")
    redis_port: str = Field("6379", env="REDIS_PORT")
    api_base_url: str = Field("http://127.0.0.1:8000/auth/v1", env="BASE_API_URL")

    @property
    def es_url(self):
        schema, addr = "http://", f"{self.es_host}:{self.es_port}"
        return addr if addr.startswith(schema) else f"{schema}{addr}"
