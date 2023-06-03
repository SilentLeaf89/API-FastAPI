from http import HTTPStatus
from collections import defaultdict
from functools import lru_cache
from typing import List, Optional

from elasticsearch import AsyncElasticsearch, NotFoundError
from fastapi import Depends, HTTPException

from redis.asyncio import Redis
import orjson

from db.elastic import get_elastic
from db.redis import get_redis
from models.role import Role
from schemas.person import Person, MovieRoles
from schemas.movie_short import MovieShort
from models._orjson import orjson_dumps
from services.movie import MovieService
from services.query_to_es.search_person import search_person_query
from services.query_to_es.roles_from_movie import search_roles_from_movie
from core.get_logger import get_logger


PERSON_CACHE_EXPIRE_IN_SECONDS = 5 * 60  # 5 минут
FIND_PERSONS_CACHE_EXPIRE_IN_SECONDS = 60  # 1 минута
logger = get_logger()


class PersonService:
    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        self.redis = redis
        self.elastic = elastic

    # persons/{uuid}
    async def get_by_id(self, person_id: str) -> Optional[Person]:
        person = await self._person_from_cache(person_id)
        if not person:
            role = await self._get_person_from_elastic(person_id)
            if not role:
                return None
            movie_roles = await self._get_movie_roles_from_elastic(person_id)
            person = Person(
                uuid=role.id,
                full_name=role.full_name,
                movies=movie_roles)
            await self._put_person_to_cache(person)
        return person

    async def _get_person_from_elastic(
            self,
            person_id: str
            ) -> Optional[Role]:
        try:
            doc = await self.elastic.get('person', person_id)
        except NotFoundError:
            return None
        logger.info('Person {0} request from ES'.format(person_id))
        return Role(**doc['_source'])

    async def _get_movie_roles_from_elastic(
            self,
            person_id: str
            ) -> Optional[List[MovieRoles]]:
        try:
            body = search_roles_from_movie(person_id)
            response = (await self.elastic.search(
                body=body,
                index='movies',
                size=100
                ))['hits']['hits']
            movie_by_person = defaultdict(list)

            # наполнение ролями каждый фильм Персоны
            for movie in response:  # по найденным Movie
                for role in movie['_source']:  # из найденых ролей
                    for person in movie['_source'][role]:  # из всех id
                        if person_id == person['id']:  # добавляй подходящие
                            movie_by_person[movie['_id']].append(role)

            # валидируем данные
            movie_roles = []
            for id, roles in movie_by_person.items():
                movie_roles.append(MovieRoles(**{'uuid': id, 'roles': roles}))

        except NotFoundError:
            return None
        logger.info("Movie list person's {0} request from ES".format(
            person_id
            )
        )
        return movie_roles

    async def _person_from_cache(self, person_id: str) -> Optional[Person]:
        data = await self.redis.get(person_id)
        if not data:
            return None
        person = Person.parse_raw(data)
        logger.info('Person {0} get from redis'.format(person_id))
        return person

    async def _put_person_to_cache(self, person):
        await self.redis.set(
            str(person.uuid),
            person.json(),
            PERSON_CACHE_EXPIRE_IN_SECONDS
            )
        logger.info(
            'Person {0} put into redis for {1} seconds'.format(
                str(person.uuid),
                PERSON_CACHE_EXPIRE_IN_SECONDS
                )
            )

    # persons/search
    async def get_find_persons(
            self,
            query: str,
            page_number: int,
            page_size: int
            ) -> Optional[List[Person]]:
        find_persons = await self._find_persons_from_cache(
            key=f'{query}_{page_number}_{page_size}'
            )
        if not find_persons:
            find_id = await self.get_find_persons_from_elastic(
                query,
                page_number,
                page_size
                )
            find_persons = []
            for id in find_id:
                find_persons.append(await self.get_by_id(id))

        if not find_persons:
            return None
        await self._put_find_persons_to_cache(
            key=f'{query}_{page_number}_{page_size}',
            find_persons=find_persons)
        return find_persons

    async def get_find_persons_from_elastic(
            self,
            query: str,
            page_number: int,
            page_size: int
            ) -> Optional[List[str]]:
        try:
            find_id = []
            body = search_person_query(query, page_number, page_size)
            response = await self.elastic.search(
                body=body,
                index='person',
                size=page_size
                )
            logger.info(
                'Persons list on demand {0} request from ES'.format(query)
            )
            docs = response['hits']['hits']
            find_id = []
            for doc in docs:
                find_id.append(doc['_id'])

        except NotFoundError:
            return None
        return find_id

    async def _find_persons_from_cache(
            self,
            key: str
            ) -> Optional[List[Person]]:
        values = await self.redis.get(key)
        if not values:
            return None
        values = orjson.loads(values)
        data = []
        for person in values:
            data.append(Person.parse_raw(person))
        logger.info('Persons list by {0} get from redis'.format(key))
        return data

    async def _put_find_persons_to_cache(
            self,
            key: str,
            find_persons: Optional[List[Person]]
            ):
        values = []
        for person in find_persons:
            values.append(person.json())

        await self.redis.set(
            key,
            orjson_dumps(values, default='default'),
            FIND_PERSONS_CACHE_EXPIRE_IN_SECONDS
            )
        logger.info(
            'Persons list by {0} put into redis for {1} seconds'.format(
                key,
                FIND_PERSONS_CACHE_EXPIRE_IN_SECONDS
                )
            )

    # persons/<uuid>/movies
    async def get_movies_by_person(
            self,
            uuid: str,
            movie_service: MovieService
            ) -> Optional[List[Person]]:

        response_movies = await movie_service._find_movies_from_cache(
            uuid+'_movies'
            )
        if not response_movies:
            person = await self.get_by_id(uuid)  # Person
            if not person:
                return None
            movie_id = []
            for movie in person.movies:
                movie_id.append(str(movie.uuid))
            if not movie_id:
                raise HTTPException(
                    status_code=HTTPStatus.NOT_FOUND,
                    detail='Movies by {} not found'.format(person.full_name)
                    )
            response_movies = []
            for id in movie_id:
                movie = await movie_service.get_by_id(id)
                movie_by_person = MovieShort(
                    uuid=movie.id,
                    imdb_rating=movie.imdb_rating,
                    title=movie.title
                    )
                response_movies.append(movie_by_person)

        await movie_service._put_find_movies_to_cache(
            uuid+'_movies',
            response_movies
            )
        return response_movies


@lru_cache()
def get_person_service(
        redis: Redis = Depends(get_redis),
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> PersonService:
    return PersonService(redis, elastic)
