import uvicorn
from elasticsearch import AsyncElasticsearch
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from redis.asyncio import Redis

from api.v1 import movies, genres, persons
from core.config import RedisSettings, ElasticSettings, PROJECT_NAME
from core.get_logger import get_logger
from db import elastic, redis


app = FastAPI(
    title=PROJECT_NAME,
    docs_url='/api/openapi',
    openapi_url='/api/openapi.json',
    default_response_class=ORJSONResponse,
    description="Информация о фильмах, жанрах и людях, \
      участвовавших в создании произведения",
    version="1.0.0"
)

logger = get_logger()


@app.on_event('startup')
async def startup():
    redis_settings = RedisSettings()
    redis.redis = Redis(
        host=redis_settings.REDIS_HOST,
        port=redis_settings.REDIS_PORT
        )
    elastic_settings = ElasticSettings()
    elastic.es = AsyncElasticsearch(
        hosts=[
            f'{elastic_settings.ELASTIC_HOST}:{elastic_settings.ELASTIC_PORT}'
            ]
        )
    logger.info('redis and elasticsearch startup')


@app.on_event('shutdown')
async def shutdown():
    await redis.redis.close()
    await elastic.es.close()
    logger.info('redis and elasticsearch shutdown')


app.include_router(movies.router, prefix='/api/v1/movies', tags=['Фильмы'])
app.include_router(genres.router, prefix='/api/v1/genres', tags=['Жанры'])
app.include_router(persons.router, prefix='/api/v1/persons', tags=['Персоны'])

if __name__ == '__main__':
    uvicorn.run(
        'main:app',
        host='0.0.0.0',
        port=8000,
    )
