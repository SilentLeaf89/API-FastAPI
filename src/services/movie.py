from functools import lru_cache
from typing import Optional

from elasticsearch import AsyncElasticsearch, NotFoundError
from fastapi import Depends
from redis.asyncio import Redis

from db.elastic import get_elastic
from db.redis import get_redis
from models.movie import Movie

MOVIE_CACHE_EXPIRE_IN_SECONDS = 60 * 5  # 5 минут


class MovieService:
    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        self.redis = redis
        self.elastic = elastic

    async def get_by_id(self, movie_id: str) -> Optional[Movie]:
        film = await self._movie_from_cache(movie_id)
        if not film:
            film = await self._get_movie_from_elastic(movie_id)
            if not film:
                return None
            await self._put_movie_to_cache(film)
        return film

    async def _get_movie_from_elastic(self, movie_id: str) -> Optional[Movie]:
        try:
            doc = await self.elastic.get('movies', movie_id)
        except NotFoundError:
            return None
        return Movie(**doc['_source'])

    async def _movie_from_cache(self, movie_id: str) -> Optional[Movie]:
        data = await self.redis.get(movie_id)
        if not data:
            return None
        movie = Movie.parse_raw(data)
        return movie

    async def _put_movie_to_cache(self, movie: Movie):
        await self.redis.set(
            movie.id,
            movie.json(),
            MOVIE_CACHE_EXPIRE_IN_SECONDS
            )


@lru_cache()
def get_movie_service(
        redis: Redis = Depends(get_redis),
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> MovieService:
    return MovieService(redis, elastic)
