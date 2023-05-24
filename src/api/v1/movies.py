from http import HTTPStatus
from typing import List

from fastapi import APIRouter, Depends, HTTPException

from services.movie import MovieService, get_movie_service
from models.movie import Movie, ShortMovie


router = APIRouter()


@router.get('/{movie_id}', response_model=Movie,
            summary="Данные о фильме",
            response_description="Полная информация о фильме",
            tags=['Фильмы'])
async def movie_details(
        movie_id: str,
        movie_service: MovieService = Depends(get_movie_service)
        ) -> Movie:
    movie = await movie_service.get_by_id(movie_id)
    if not movie:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='Movie not found')
    return Movie(**movie)


# не готово, нужны query в ES
@router.get("/search/",
            response_model=List[ShortMovie],
            summary="Поиск кинопроизведений",
            description="Полнотекстовый поиск по кинопроизведениям",
            response_description="Название и рейтинг фильма",
            tags=['Фильмы', 'Персоны', 'Поиск']
            )
async def movie_search():
    pass


# не готово, нужны query в ES
@router.get('/',
            response_model=List[ShortMovie],
            summary="Главная страница",
            description="Главная страница сайта с 'рекомендациями'",
            response_description="Перечень отфильтрованных фильмов",
            tags=['Фильмы']
            )
async def get_index(
        sort,
        genre,
        movie_service: MovieService = Depends(get_movie_service)
        ) -> List[ShortMovie]:
    print(movie_service, sort, genre)
    pass
