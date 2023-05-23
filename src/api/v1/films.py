from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException

from services.movie import MovieService, get_movie_service
from models.movie import Movie


router = APIRouter()


# Внедряем FilmService с помощью Depends(get_film_service)
@router.get('/{movie_id}', response_model=Movie)
async def movie_details(
        movie_id: str,
        movie_service: MovieService = Depends(get_movie_service)
        ) -> Movie:
    movie = await movie_service.get_by_id(movie_id)
    if not movie:
        # Если фильм не найден, отдаём 404 статус
        # Желательно пользоваться уже определёнными HTTP-статусами,
        # которые содержат enum
        # Такой код будет более поддерживаемым
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='movie not found')

    # Перекладываем данные из models.Movie в Movie
    # Обратите внимание, что у модели бизнес-логики есть поле description
    # Которое отсутствует в модели ответа API.
    # Если бы использовалась общая модель для бизнес-логики
    # и формирования ответов API
    # вы бы предоставляли клиентам данные, которые им не нужны
    # и, возможно, данные, которые опасно возвращать
    return Movie(id=movie.id, title=movie.title)
