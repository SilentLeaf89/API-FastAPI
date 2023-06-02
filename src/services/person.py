from functools import lru_cache
from typing import List, Optional

from elasticsearch import AsyncElasticsearch, NotFoundError
from fastapi import Depends
from redis.asyncio import Redis
import orjson

from db.elastic import get_elastic
from db.redis import get_redis
from models.role import Role
from schemas.person import Person, MovieRoles
from models._orjson import orjson_dumps
from services.query_to_es.search_person import search_person_query
from services.query_to_es.movie_roles import search_movie_roles
from core.get_logger import get_logger


PERSON_CACHE_EXPIRE_IN_SECONDS = 60 * 5  # 5 минут
FIND_PERSONS_CACHE_EXPIRE_IN_SECONDS = 60 * 1  # 1 минута
logger = get_logger()


class PersonService:
    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        self.redis = redis
        self.elastic = elastic

    # Person. Ручка /{uuid} и вторая часть /persons/search
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
            roles = ["actors", "directors", "writers"]
            response = {}
            bodies = {}
            for role in roles:
                body = search_movie_roles(role, person_id)
                bodies[role] = body
                response[role] = (await self.elastic.search(
                    body=body,
                    index='movies',
                    size=100
                    ))['hits']['hits']

            # uniq id movies
            movie_list = []
            for role in roles:
                role_by_movie = response[role]
                for movie in role_by_movie:
                    movie_list.append(movie['_id'])
            uniq_uuid = set(movie_list)

            # {<id> : [],}
            movie_by_person = {}
            for id_movie in uniq_uuid:
                movie_by_person[id_movie] = []

            # наполнение ролями каждый фильм Персоны
            for role in roles:
                role_by_movie = response[role]
                for movie in role_by_movie:
                    if movie['_id'] in uniq_uuid:
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

    # List[id]. Первая часть ручки /persons/search
    async def get_find_persons(
            self,
            query: str
            ) -> Optional[List[str]]:
        find_id = await self._find_persons_from_cache(query)
        if not find_id:
            find_id = await self.get_find_persons_from_elastic(query)
            if not find_id:
                return None
            await self._put_find_persons_to_cache(query, find_id)
        return find_id

    async def get_find_persons_from_elastic(
            self,
            query: str
            ) -> Optional[List[str]]:
        try:
            find_id = []
            body = search_person_query(query)
            response = await self.elastic.search(
                body=body,
                index='person',
                size=100
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
            query: str
            ) -> Optional[List[str]]:
        data = await self.redis.get(query)
        if not data:
            return None
        data = orjson.loads(data)
        logger.info('Persons list by {0} get data: {1} from redis'.format(
            query,
            data)
        )
        return data

    async def _put_find_persons_to_cache(
            self,
            query: str,
            find_id: Optional[List[str]]
            ):
        await self.redis.set(
            query,
            orjson_dumps(find_id, default='default'),
            FIND_PERSONS_CACHE_EXPIRE_IN_SECONDS
            )
        logger.info(
            'Persons list by {0} with data: {1} \
             put into redis for {2} seconds'.format(
                query,
                find_id,
                FIND_PERSONS_CACHE_EXPIRE_IN_SECONDS
                )
            )


@lru_cache()
def get_person_service(
        redis: Redis = Depends(get_redis),
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> PersonService:
    return PersonService(redis, elastic)
