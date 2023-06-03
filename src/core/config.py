import os

from pydantic import BaseSettings, Field


# Название проекта. Используется в Swagger-документации
PROJECT_NAME = os.getenv('PROJECT_NAME', 'movies')

# Корень проекта
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class LogSettings(BaseSettings):
    LOG_LOGGER_LEVEL: str = Field('INFO', env='LOG_LOGGER_LEVEL')
    LOG_ROOT_LEVEL: str = Field('INFO', env='LOG_ROOT_LEVEL')
    LOG_HANDLERS_LEVEL: str = Field('DEBUG', env='LOG_HANDLERS_LEVEL')

    class Config:
        env_file = '.env.settings'
        env_file_encoding = 'utf-8'


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
