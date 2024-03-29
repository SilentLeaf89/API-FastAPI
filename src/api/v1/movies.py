from http import HTTPStatus
from typing import Annotated, List
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query

from services.movie import MovieService, get_movie_service
from schemas.movie_short import MovieShort
from schemas.movie_info import MovieInfo
from services.sorting import sorting


router = APIRouter()


@router.get('/{movie_id}', response_model=MovieInfo,
            summary="Данные о фильме",
            response_description="Полная информация о фильме",
            tags=['Фильмы'])
async def movie_details(
        movie_id: str,
        movie_service: MovieService = Depends(get_movie_service)
        ) -> MovieInfo:
    movie = await movie_service.get_by_id(movie_id)
    if not movie:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='Movie not found')
    return MovieInfo(
        uuid=movie.id,
        title=movie.title,
        imdb_rating=movie.imdb_rating,
        description=movie.description,
        genre=movie.genre,
        actors=movie.actors,
        writers=movie.writers,
        directors=movie.directors
        )


@router.get("/search/",
            response_model=List[MovieShort],
            summary="Поиск кинопроизведений",
            description="Полнотекстовый поиск по кинопроизведениям",
            response_description="Название и рейтинг фильма",
            tags=['Фильмы', 'Поиск']
            )
async def movie_search(
        query: str,
        movie_service: MovieService = Depends(get_movie_service),
        page_number: Annotated[int, Query(1, ge=1, lt=200)] = 1,
        page_size: Annotated[int, Query(50, ge=10, lt=100)] = 50
        ) -> List[MovieShort]:

    find_movies = await movie_service.get_find_movies(
        query,
        page_number,
        page_size
        )
    if not find_movies:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='Movies not found, Sorry')

    return find_movies


@router.get('/',
            response_model=List[MovieShort],
            summary="Главная страница",
            description="Главная страница сайта с 'рекомендациями'",
            response_description="Перечень отфильтрованных фильмов",
            tags=['Фильмы']
            )
async def get_index(
        genre: uuid.UUID = None,
        movie_service: MovieService = Depends(get_movie_service),
        sort: str = "-imdb_rating",
        page_number: Annotated[int, Query(1, ge=1, lt=200)] = 1,
        page_size: Annotated[int, Query(50, ge=10, lt=100)] = 50
        ) -> List[MovieShort]:

    order, sorted_field = sorting(sort)
    if genre:
        sorted_movies = await movie_service.get_genres_sorted_movies(
            order,
            sorted_field,
            page_number,
            page_size,
            genre
            )
    else:
        sorted_movies = await movie_service.get_sorted_movies(
            order,
            sorted_field,
            page_number,
            page_size,
            )
    if not sorted_movies:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='If you see this page: we are failed, sorry')

    return sorted_movies
