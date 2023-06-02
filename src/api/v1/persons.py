from http import HTTPStatus
from typing import List

from fastapi import APIRouter, Depends, HTTPException

from services.person import PersonService, get_person_service
from services.movie import MovieService, get_movie_service
from services.paginator import Paginator
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
async def get_movies_by_person(
        uuid: str,
        person_service: PersonService = Depends(get_person_service),
        movie_service: MovieService = Depends(get_movie_service)
        ) -> List[MovieShort]:
    # соберем id всех фильмов персоны
    person = await person_service.get_by_id(uuid)  # Person
    movie_id = []
    for movie in person.movies:
        movie_id.append(str(movie.uuid))

    # соберем все MovieShort по id
    response_movies = []
    for id in movie_id:
        movie = await movie_service.get_by_id(id)
        movie_by_person = MovieShort(
            uuid=movie.id,
            imdb_rating=movie.imdb_rating,
            title=movie.title
            )
        response_movies.append(movie_by_person)
    if not response_movies:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='Movies not found')
    return response_movies


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
        page_number: int = 1,
        page_size: int = 50
        ) -> List[Person]:

    # find_persons - List[id]
    find_persons = await person_service.get_find_persons(query)

    if not find_persons:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='Person not found')
    response_persons = []
    for id in find_persons:
        response_persons.append(await person_service.get_by_id(id))
    paginator = Paginator(
        items=response_persons,
        page_number=page_number,
        page_size=page_size
        )
    return paginator.paginate()
