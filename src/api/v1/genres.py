from http import HTTPStatus
from typing import List

from fastapi import APIRouter, Depends, HTTPException

from services.genre import GenreService, get_genre_service
from schemas.genre import Genre


router = APIRouter()


@router.get('/{uuid}',
            response_model=Genre,
            summary="Информация о жанре",
            description="Полная информация о жанре",
            response_description="Жанр и его описание",
            tags=['Жанры'])
async def genre_details(
        uuid: str,
        genre_service: GenreService = Depends(get_genre_service)
        ) -> Genre:
    genre = await genre_service.get_by_id(uuid)
    if not genre:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='genre not found')
    return Genre(
        uuid=genre.id,
        name=genre.name,
        description=genre.description
        )


@router.get('/',
            response_model=List[Genre],
            summary="Информация о жанрах",
            description="Полная информация о всех жанрах",
            response_description="Жанры и их описания",
            tags=['Жанры'])
async def get_all_genres(
        genre_service: GenreService = Depends(get_genre_service)
        ) -> List[Genre]:
    genres = await genre_service.get_all_genres()
    if not genres:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='genre not found')
    genres_api = []
    for genre in genres:
        genres_api.append(
            Genre(
                uuid=genre.id,
                name=genre.name,
                description=genre.description
                )
            )
    return genres_api
