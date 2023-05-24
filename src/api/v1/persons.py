from http import HTTPStatus
from typing import List

from fastapi import APIRouter, Depends, HTTPException

from services.person import PersonService, get_person_service
from models.role import Role
from models.movie import ShortMovie


router = APIRouter()


# готово
@router.get('/{uuid}', response_model=Role)
async def person_details(
        uuid: str,
        person_service: PersonService = Depends(get_person_service)
        ) -> Role:
    person = await person_service.get_by_id(uuid)
    if not person:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Такой персоны не найдено')

    return Role(uuid=person.id,
                full_name=person.full_name,
                movies=person.movies
                )


# вероятно готово, нужен корректный ответ в movies_person_es
@router.get('/{uuid}/movie/', response_model=List[ShortMovie])
async def get_movies_by_person(
        person_service: PersonService = Depends(get_person_service)
        ) -> List[Role]:
    movies_person_es = await person_service.get_movies_by_person()
    if not movies_person_es:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='genre not found')

    movies_person = []
    for movie in movies_person_es:
        movies_person.append(ShortMovie(**movie))

    return movies_person
