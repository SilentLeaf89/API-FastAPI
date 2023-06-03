from http import HTTPStatus
from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException, Query

from services.person import PersonService, get_person_service
from services.movie import MovieService, get_movie_service
from schemas.movie_short import MovieShort
from schemas.person import Person


router = APIRouter()


@router.get('/{uuid}',
            response_model=Person,
            summary="Информация о персоне",
            description="Полная информация о актере, сценаристе или режиссере",
            response_description="Персона и его фильмы",
            tags=['Персоны']
            )
async def person_details(
        uuid: str,
        person_service: PersonService = Depends(get_person_service)
        ) -> Person:
    person = await person_service.get_by_id(uuid)  # Person
    if not person:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Person not found')

    return person


@router.get(
        '/{uuid}/movie/',
        response_model=List[MovieShort],
        summary="Фильмы персоны",
        description="Краткие сведения о фильмах персоны",
        response_description="Список фильмов персоны",
        tags=['Персоны', 'Фильмы']
        )
async def movies_by_person(
        uuid: str,
        person_service: PersonService = Depends(get_person_service),
        movie_service: MovieService = Depends(get_movie_service)
        ) -> List[MovieShort]:

    return await person_service.get_movies_by_person(uuid, movie_service)


@router.get('/search/',
            response_model=List[Person],
            summary="Поиск персон",
            description="Поиск по актерам, сценаристам и режиссерам",
            response_description="Найденные персоны и их фильмы",
            tags=['Персоны', 'Поиск']
            )
async def persons_search(
        query: str,
        person_service: PersonService = Depends(get_person_service),
        page_number: Annotated[int, Query(1, ge=1, lt=200)] = 1,
        page_size: Annotated[int, Query(50, ge=10, lt=100)] = 50
        ) -> List[Person]:

    find_persons = await person_service.get_find_persons(
        query,
        page_number,
        page_size
        )

    if not find_persons:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='Person not found')

    return find_persons
