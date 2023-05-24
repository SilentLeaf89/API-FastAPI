from functools import lru_cache
from typing import List, Optional

from elasticsearch import AsyncElasticsearch, NotFoundError
from fastapi import Depends
from redis.asyncio import Redis

from db.elastic import get_elastic
from db.redis import get_redis
from models.genre import Genre

GENRE_CACHE_EXPIRE_IN_SECONDS = 60 * 5  # 5 минут


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
            doc = await self.elastic.get('genre', genre_id)
        except NotFoundError:
            return None
        return Genre(**doc['_source'])

    async def _genre_from_cache(self, genre_id: str) -> Optional[Genre]:
        data = await self.redis.get(genre_id)
        if not data:
            return None
        genre = Genre.parse_raw(data)
        return genre

    async def _put_genre_to_cache(self, genre: Genre):
        await self.redis.set(
            genre.id,
            genre.json(),
            GENRE_CACHE_EXPIRE_IN_SECONDS
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
            genres_es = await self.elastic.search(
                index='genre'
                )['hits']['hits']
            for genre in genres_es:
                genres.append(Genre(**genre))
        except NotFoundError:
            return None
        return genres

    async def _genres_from_cache(self) -> Optional[List[Genre]]:
        data = await self.redis.get('genres')
        if not data:
            return None
        genres = []
        for genre in data:
            genres.append(Genre.parse_raw(genre))
        return genres

    async def _put_genres_to_cache(self, genres: List[Genre]):
        await self.redis.set(
            genres,
            genres.json(),
            GENRE_CACHE_EXPIRE_IN_SECONDS
            )


@lru_cache()
def get_genre_service(
        redis: Redis = Depends(get_redis),
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> GenreService:
    return GenreService(redis, elastic)
