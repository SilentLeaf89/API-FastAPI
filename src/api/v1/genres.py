from http import HTTPStatus
from typing import List

from fastapi import APIRouter, Depends, HTTPException

from services.genre import GenreService, get_genre_service
from models.genre import Genre


router = APIRouter()


# готово
@router.get('/{uuid}', response_model=Genre)
async def genre_details(
        uuid: str,
        genre_service: GenreService = Depends(get_genre_service)
        ) -> Genre:
    genre = await genre_service.get_by_id(uuid)
    if not genre:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='genre not found')

    return Genre(uuid=genre.id,
                 name=genre.name,
                 description=genre.description,
                 popularity=genre.popularity
                 )


# нужен только popularity в ES (вариант: высчитывать в etl pg->es)
@router.get('/', response_model=List[Genre])
async def get_all_genres(
        genre_service: GenreService = Depends(get_genre_service)
        ) -> List[Genre]:
    genres = await genre_service.get_all_genres_from_elastic()
    if not genres:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='genre not found')

    return Genre(uuid=genres._id,
                 name=genres.name,
                 description=genres.description,
                 popularity=genres.popularity  # пока такого поля нет, но будет
                 )
