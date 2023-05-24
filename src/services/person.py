from functools import lru_cache
from typing import List, Optional

from elasticsearch import AsyncElasticsearch, NotFoundError
from fastapi import Depends
from redis.asyncio import Redis

from db.elastic import get_elastic
from db.redis import get_redis
from models.role import Role
from models.movie import ShortMovie


PERSON_CACHE_EXPIRE_IN_SECONDS = 60 * 5  # 5 минут


class PersonService:
    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        self.redis = redis
        self.elastic = elastic

    # ручка /{uuid}
    async def get_by_id(self, person_id: str) -> Optional[Role]:
        person = await self._person_from_cache(person_id)
        if not person:
            person = await self._get_person_from_elastic(person_id)
            if not person:
                return None
            await self._put_person_to_cache(person)
        return person

    # не реализовано!
    # нужен корректный запрос в ES,чтобы получить все фильмы персоны
    async def _get_person_from_elastic(self, person_id: str) -> Optional[Role]:
        try:
            person = await self.elastic.get('person', person_id)
            movies = await self.elastic.get('person', person_id)  # !!!
            person['movies'] = movies
        except NotFoundError:
            return None
        return Role(**person['_source'])

    async def _person_from_cache(self, person_id: str) -> Optional[Role]:
        data = await self.redis.get(person_id)
        if not data:
            return None
        person = Role.parse_raw(data)
        return person

    async def _put_person_to_cache(self, person: Role):
        await self.redis.set(
            person.id,
            person.json(),
            PERSON_CACHE_EXPIRE_IN_SECONDS
            )

    # ручка /{uuid}/movie/
    async def get_movies_by_person(
            self,
            person_id: str
            ) -> Optional[List[ShortMovie]]:
        movies_by_person = await self._movies_by_person_from_cache(person_id)
        if not movies_by_person:
            movies_by_person = await self._get_person_from_elastic(person_id)
            if not movies_by_person:
                return None
            await self._put_movies_by_person_to_cache(movies_by_person)
        return movies_by_person

    # нужен запрос в ES
    async def _get_movies_by_person_from_elastic(
            self,
            person_id: str
            ) -> Optional[Role]:
        try:
            # что-то
            movies_by_person = await self.elastic.get('person', person_id)  # !
        except NotFoundError:
            return None
        return Role(**movies_by_person['_source'])

    async def _movies_by_person_from_cache(self, person_id: str) -> Optional[Role]:
        data = await self.redis.get(movies_by_person)
        if not data:
            return None
        movies_by_person = Role.parse_raw(data)
        return movies_by_person

    async def _put_person_to_cache(self, person: Role):
        await self.redis.set(
            person.id,
            person.json(),
            PERSON_CACHE_EXPIRE_IN_SECONDS
            )


@lru_cache()
def get_person_service(
        redis: Redis = Depends(get_redis),
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> PersonService:
    return PersonService(redis, elastic)
