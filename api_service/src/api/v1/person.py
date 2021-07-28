from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException, Request, Query

from models.person import Person
from services.person import PersonService, get_person_service
from utils import request_to_str

router = APIRouter()


@router.get("/{person_id}", response_model=Person)
async def person_details(
        request: Request,
        person_id: str,
        person_service: PersonService = Depends(get_person_service),
) -> Person:
    """
    Возвращает детальную информацию об участнике.
    """
    person = await person_service.get_by_id(request_to_str(request), person_id)
    if not person:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="person not found")
    return person


@router.get("/search/")
async def search_persons(
    request: Request,
    query: str,
    page_number: int = Query(0, ge=0),
    page_size: int = Query(50, ge=0),
    person_service: PersonService = Depends(get_person_service),
) -> list[Person]:
    """
    :param query:
    :param page_size:
    :param page_number:
    :param film_service:
    """
    return await person_service.search_persons(
        request_to_str(request),
        query=query,
        page_number=page_number,
        page_size=page_size,
    )
