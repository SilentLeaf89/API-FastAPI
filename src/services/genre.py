from functools import lru_cache
from typing import List, Optional

from elasticsearch import AsyncElasticsearch, NotFoundError
from fastapi import Depends
import orjson
from redis.asyncio import Redis

from db.elastic import get_elastic
from db.redis import get_redis
from models.genre import Genre
from models._orjson import orjson_dumps
from core.get_logger import get_logger

GENRE_CACHE_EXPIRE_IN_SECONDS = 60 * 5  # 5 минут
logger = get_logger()


class GenreService:
    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        self.redis = redis
        self.elastic = elastic

    # один жанр
    async def get_by_id(self, genre_id: str) -> Optional[Genre]:
        genre = await self._genre_from_cache(genre_id)
        if not genre:
            genre = await self._get_genre_from_elastic(genre_id)
            if not genre:
                return None
            await self._put_genre_to_cache(genre)
        return genre

    async def _get_genre_from_elastic(self, genre_id: str) -> Optional[Genre]:
        try:
            doc = await self.elastic.get('genres', genre_id)
            logger.info('Genre {0} request from ES'.format(genre_id))
        except NotFoundError:
            return None
        return Genre(**doc['_source'])

    async def _genre_from_cache(self, genre_id: str) -> Optional[Genre]:
        data = await self.redis.get(genre_id)
        if not data:
            return None
        genre = Genre.parse_raw(data)
        logger.info('Genre {0} get from redis'.format(genre_id))
        return genre

    async def _put_genre_to_cache(self, genre: Genre):
        await self.redis.set(
            str(genre.id),
            genre.json(),
            GENRE_CACHE_EXPIRE_IN_SECONDS
            )
        logger.info(
            'Genre {0} put into redis for {1} seconds'.format(
                str(genre.id),
                GENRE_CACHE_EXPIRE_IN_SECONDS
                )
            )

    # все жанры
    async def get_all_genres(self) -> Optional[List[Genre]]:
        genres = await self._genres_from_cache()
        if not genres:
            genres = await self._get_all_genres_from_elastic()
            if not genres:
                return None
            await self._put_genres_to_cache(genres)
        return genres

    async def _get_all_genres_from_elastic(self) -> List[Genre]:
        try:
            genres = []
            genres_es = (await self.elastic.search(
                index='genres'
                ))['hits']['hits']
            logger.info('all genres request from ES')
            for genre in genres_es:
                genres.append(Genre(**genre['_source']))
        except NotFoundError:
            return None
        return genres

    async def _genres_from_cache(self) -> Optional[List[Genre]]:
        data = await self.redis.get('genres')
        if not data:
            return None
        data = orjson.loads(data)
        genres = []
        for genre in data:
            genres.append(Genre.parse_raw(genre))
        logger.info('all genres get from redis')
        return genres

    async def _put_genres_to_cache(self, genres: List[Genre]):
        genres_dump = []
        for genre in genres:
            genres_dump.append(genre.json())

        data = orjson_dumps(genres_dump, default='default')

        await self.redis.set(
            'genres',
            data,
            GENRE_CACHE_EXPIRE_IN_SECONDS
            )
        logger.info(
            'list of all genres put into redis for {0} seconds'.format(
                GENRE_CACHE_EXPIRE_IN_SECONDS
                )
            )


@lru_cache()
def get_genre_service(
        redis: Redis = Depends(get_redis),
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> GenreService:
    return GenreService(redis, elastic)
