from http import HTTPStatus
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request

from models.genre import Genre
from services.genre import GenreService, get_genre_service
from utils import request_to_str

router = APIRouter()


@router.get("/{genre_id}")
async def genre_details(
    request: Request,
    genre_id: str,
    genre_service: GenreService = Depends(get_genre_service),
) -> Optional[Genre]:
    """
    Возвращает подробную информацию о жанре.

    :param genre_id: идентификатор жанра.
    :param genre_service: TODO
    :return:
    """
    if genre := await genre_service.get_by_id(request_to_str(request), genre_id):
        return genre
    raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="genre not found")


@router.get("/")
async def genre_list(
    request: Request, genre_service: GenreService = Depends(get_genre_service),
) -> list[Genre]:
    """
    Возвращает список всех доступных жанров.

    :param genre_service: TODO
    :return:
    """
    return await genre_service.genre_list(request_to_str(request))
