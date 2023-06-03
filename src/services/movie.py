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
from schemas.movie_short import MovieShort


MOVIE_CACHE_EXPIRE_IN_SECONDS = 5 * 60  # 5 минут
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
            query: str,
            page_number,
            page_size
            ) -> Optional[List[MovieShort]]:
        find_movies = await self._find_movies_from_cache(
            key=f'{query}_{page_number}_{page_size}'
            )
        if not find_movies:
            find_movies = await self._get_find_movies_from_elastic(
                query,
                page_number,
                page_size
                )
            if not find_movies:
                return None
            await self._put_find_movies_to_cache(
                key=f'{query}_{page_number}_{page_size}',
                find_movies=find_movies
                )
        return find_movies

    async def _get_find_movies_from_elastic(
            self,
            query: str,
            page_number: int,
            page_size: int
            ) -> Optional[List[str]]:
        try:
            find_movies = []

            body = search_movie_query(query, page_number, page_size)
            response = await self.elastic.search(
                body=body,
                index='movies',
                size=page_size
                )
            logger.info(
                'Movies list on demand {0} request from ES'.format(query)
            )
            docs = response['hits']['hits']
            find_movies = []
            for doc in docs:
                find_movies.append(MovieShort(
                    uuid=doc['_source']['id'],
                    imdb_rating=doc['_source']['imdb_rating'],
                    title=doc['_source']['title']
                    )
                )

        except NotFoundError:
            return None
        return find_movies

    # главная
    async def get_sorted_movies(
            self,
            order: str,
            sorted_field: str,
            page_number: int,
            page_size: int,
            ) -> Optional[List[MovieShort]]:
        sorted_movies = await self._find_movies_from_cache(
            key=f'index_page_{page_number}_{page_size}'
            )
        if not sorted_movies:
            sorted_movies = await self._get_sorted_movies_from_elastic(
                order,
                sorted_field,
                page_number,
                page_size
                )
            if not sorted_movies:
                return None
            await self._put_find_movies_to_cache(
                key=f'index_page_{page_number}_{page_size}',
                find_movies=sorted_movies
                )
        return sorted_movies

    async def _get_sorted_movies_from_elastic(
            self,
            order: str,
            sorted_field: str,
            page_number: int,
            page_size: int
            ) -> Optional[List[MovieShort]]:
        try:
            sorted_movies = []
            body = sorted_movie_query(
                order,
                sorted_field,
                page_number,
                page_size
                )
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
            sorted_movies = []
            for doc in docs:
                sorted_movies.append(MovieShort(
                    uuid=doc['_source']['id'],
                    imdb_rating=doc['_source']['imdb_rating'],
                    title=doc['_source']['title']
                    )
                )

        except NotFoundError:
            return None
        return sorted_movies

    async def get_genres_sorted_movies(
            self,
            order: str,
            sorted_field: str,
            page_number,
            page_size,
            genre: uuid.UUID
            ) -> Optional[List[MovieShort]]:
        genres_sorted_movies = await self._find_movies_from_cache(
            key=f'{genre}_{page_number}_{page_size}'
            )
        if not genres_sorted_movies:
            genres_sorted_movies = \
                await self._get_genres_sorted_movies_from_elastic(
                    order,
                    sorted_field,
                    page_number,
                    page_size,
                    genre
                    )
            if not genres_sorted_movies:
                return None
            await self._put_find_movies_to_cache(
                key=f'{genre}_{page_number}_{page_size}',
                find_movies=genres_sorted_movies
                )
        return genres_sorted_movies

    async def _get_genres_sorted_movies_from_elastic(
            self,
            order: str,
            sorted_field: str,
            page_number: int,
            page_size: int,
            genre: uuid.UUID
            ) -> Optional[List[MovieShort]]:
        try:
            body = genre_sorted_movie_query(
                order,
                sorted_field,
                page_number,
                page_size,
                genre
                )
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
            sorted_senres_movies = []
            for doc in docs:
                sorted_senres_movies.append(MovieShort(
                    uuid=doc['_source']['id'],
                    imdb_rating=doc['_source']['imdb_rating'],
                    title=doc['_source']['title']
                    )
                )

        except NotFoundError:
            return None
        return sorted_senres_movies

    # забрать / получить фильмы по запросу из redis
    async def _find_movies_from_cache(
            self,
            key: str
            ) -> Optional[List[str]]:
        values = await self.redis.get(key)
        if not values:
            return None
        values = orjson.loads(values)
        data = []
        for movie in values:
            data.append(MovieShort.parse_raw(movie))
        logger.info('Movies by {0} get from redis'.format(key))
        return data

    async def _put_find_movies_to_cache(
            self,
            key: str,
            find_movies: Optional[List[MovieShort]]
            ):
        values = []
        for movie in find_movies:
            values.append(movie.json())
        await self.redis.set(
            key,
            orjson_dumps(values, default='default'),
            SORTED_MOVIES_CACHE_EXPIRE_IN_SECONDS
            )
        logger.info(
            'Movies by {0} put into redis for {1} seconds'.format(
                key,
                SORTED_MOVIES_CACHE_EXPIRE_IN_SECONDS
                )
            )


@lru_cache()
def get_movie_service(
        redis: Redis = Depends(get_redis),
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> MovieService:
    return MovieService(redis, elastic)
