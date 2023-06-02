import os

from pydantic import BaseSettings, Field


# Название проекта. Используется в Swagger-документации
PROJECT_NAME = os.getenv('PROJECT_NAME', 'movies')

# Корень проекта
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Уровень логирования
LOG_LOGGER_LEVEL = os.getenv('LOG_LOGGER_LEVEL', 'info')
LOG_ROOT_LEVEL = os.getenv('LOG_ROOT_LEVEL', 'info')
LOG_HANDLERS_LEVEL = os.getenv('LOG_HANDLERS_LEVEL', 'debug')


class RedisSettings(BaseSettings):
    REDIS_HOST: str = Field('127.0.0.1', env='REDIS_HOST')
    REDIS_PORT: int = Field(6379, env='REDIS_PORT')

    class Config:
        env_file = '.env.redis'
        env_file_encoding = 'utf-8'


class ElasticSettings(BaseSettings):
    ELASTIC_HOST: str = Field('127.0.0.1', env='ELASTIC_HOST')
    ELASTIC_PORT: int = Field(9200, env='ELASTIC_PORT')

    class Config:
        env_file = '.env.elastic'
        env_file_encoding = 'utf-8'
