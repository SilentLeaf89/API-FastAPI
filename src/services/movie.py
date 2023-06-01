from functools import lru_cache
from typing import Optional, List
import uuid

from elasticsearch import AsyncElasticsearch, NotFoundError
from fastapi import Depends
from redis.asyncio import Redis
import orjson

from db.elastic import get_elastic
from db.redis import get_redis
from models.movie import Movie
from models._orjson import orjson_dumps
from services.query_to_es.search_movie import search_movie_query
from services.query_to_es.sorted_movie import sorted_movie_query
from services.query_to_es.genre_sorted_movie import genre_sorted_movie_query
from core.get_logger import get_logger


MOVIE_CACHE_EXPIRE_IN_SECONDS = 60 * 5  # 5 минут
FIND_MOVIES_CACHE_EXPIRE_IN_SECONDS = 20  # 20 секунд
SORTED_MOVIES_CACHE_EXPIRE_IN_SECONDS = 60 * 60  # 1 час
logger = get_logger()


class MovieService:
    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        self.redis = redis
        self.elastic = elastic

    # один фильм целиком
    async def get_by_id(self, movie_id: str) -> Optional[Movie]:
        movie = await self._movie_from_cache(movie_id)
        if not movie:
            movie = await self._get_movie_from_elastic(movie_id)
            if not movie:
                return None
            await self._put_movie_to_cache(movie)
        return movie

    async def _get_movie_from_elastic(
            self,
            movie_id: str
            ) -> Optional[Movie]:
        try:
            doc = await self.elastic.get('movies', movie_id)
        except NotFoundError:
            return None
        logger.info('Movie {0} request from ES'.format(movie_id))
        return Movie(**doc['_source'])

    async def _movie_from_cache(self, movie_id: str) -> Optional[Movie]:
        data = await self.redis.get(movie_id)
        if not data:
            return None
        movie = Movie.parse_raw(data)
        logger.info('Movie {0} get from redis'.format(movie_id))
        return movie

    async def _put_movie_to_cache(self, movie: Movie):
        await self.redis.set(
            str(movie.id),
            movie.json(),
            MOVIE_CACHE_EXPIRE_IN_SECONDS
            )
        logger.info(
            'Movie {0} put into redis for {1} seconds'.format(
                str(movie.id),
                MOVIE_CACHE_EXPIRE_IN_SECONDS
                )
            )

    # /movie/search
    async def get_find_movies(
            self,
            query: str
            ) -> Optional[List[Movie]]:
        find_id = await self._ids_from_cache(query)
        if not find_id:
            find_id = await self._get_find_movies_from_elastic(query)
            if not find_id:
                return None
            await self._put_ids_to_cache(query, find_id)
        return find_id

    async def _get_find_movies_from_elastic(
            self,
            query: str
            ) -> Optional[List[str]]:
        try:
            find_id = []

            body = search_movie_query(query)
            response = await self.elastic.search(
                body=body,
                index='movies',
                size=100
                )
            logger.info(
                'Movies list on demand {0} request from ES'.format(query)
            )
            docs = response['hits']['hits']
            find_id = []
            for doc in docs:
                find_id.append(doc['_id'])

        except NotFoundError:
            return None
        return find_id

    # главная
    async def get_sorted_movies(
            self,
            order: str,
            sorted_field: str
            ) -> Optional[List[Movie]]:
        sorted_id = await self._ids_from_cache('index_sorted')
        if not sorted_id:
            sorted_id = await self._get_sorted_movies_from_elastic(
                order,
                sorted_field
                )
            if not sorted_id:
                return None
            await self._put_ids_to_cache('index_sorted', sorted_id)
        return sorted_id

    async def _get_sorted_movies_from_elastic(
            self,
            order: str,
            sorted_field: str
            ) -> Optional[List[str]]:
        try:
            sorted_id = []
            body = sorted_movie_query(order, sorted_field)
            response = await self.elastic.search(
                body=body,
                index='movies',
                size=1000
                )
            logger.info(
                'Movies list with order {0} and sorted on {1} \
                 request from ES'.format(
                    order,
                    sorted_field)
            )
            docs = response['hits']['hits']
            sorted_id = []
            for doc in docs:
                sorted_id.append(doc['_id'])

        except NotFoundError:
            return None
        return sorted_id

    async def get_genres_sorted_movies(
            self,
            order: str,
            sorted_field: str,
            genre: uuid.UUID
            ) -> Optional[List[Movie]]:
        sorted_id = await self._ids_from_cache('index_genres_sorted')
        if not sorted_id:
            sorted_id = await self._get_genres_sorted_movies_from_elastic(
                order,
                sorted_field,
                genre
                )
            if not sorted_id:
                return None
            await self._put_ids_to_cache('index_genres_sorted', sorted_id)
        return sorted_id

    async def _get_genres_sorted_movies_from_elastic(
            self,
            order: str,
            sorted_field: str,
            genre: uuid.UUID
            ) -> Optional[List[str]]:
        try:
            sorted_id = []
            body = genre_sorted_movie_query(order, sorted_field, genre)
            response = await self.elastic.search(
                body=body,
                index='movies',
                size=1000
                )
            logger.info(
                'Movies list with order {0} and genre {2} \
                   sorted on {1} request from ES'.format(
                    order,
                    sorted_field,
                    genre)
            )
            docs = response['hits']['hits']
            sorted_id = []
            for doc in docs:
                sorted_id.append(doc['_id'])

        except NotFoundError:
            return None
        return sorted_id

    # забрать / получить список id из redis
    async def _ids_from_cache(
            self,
            key: str
            ) -> Optional[List[str]]:
        data = await self.redis.get(key)
        if not data:
            return None
        data = orjson.loads(data)
        logger.info('Movies list by {0} get data: {1} from redis'.format(
            key,
            data)
        )
        return data

    async def _put_ids_to_cache(
            self,
            key: str,
            ids: Optional[List[str]]
            ):
        await self.redis.set(
            key,
            orjson_dumps(ids, default='default'),
            SORTED_MOVIES_CACHE_EXPIRE_IN_SECONDS
            )
        logger.info(
            'Movies list by {0} with data: {1} \
             put into redis for {2} seconds'.format(
                key,
                ids,
                SORTED_MOVIES_CACHE_EXPIRE_IN_SECONDS
                )
            )


@lru_cache()
def get_movie_service(
        redis: Redis = Depends(get_redis),
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> MovieService:
    return MovieService(redis, elastic)
