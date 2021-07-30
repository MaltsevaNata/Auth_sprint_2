from http import HTTPStatus
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request

from models.filmwork import FilmWork
from services.filmwork import FilmService, get_film_service
from utils import request_to_str

router = APIRouter()


@router.get("/{film_id}", response_model=FilmWork)
async def film_details(
    request: Request,
    film_id: str,
    film_service: FilmService = Depends(get_film_service),
) -> FilmWork:
    """
    Возвращает детальную информацию о фильме.
    """
    film = await film_service.get_by_id(request_to_str(request), film_id)
    if not film:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="film not found")
    return film


@router.get("/")
async def films(
    request: Request,
    page_number: int = Query(0, ge=0),
    page_size: int = Query(50, ge=0),
    sort: str = Query("imdb_rating", regex="-?imdb_rating$"),
    genre: Optional[str] = None,
    film_service: FilmService = Depends(get_film_service),
) -> list[FilmWork]:
    """
    Возвращает информацию о фильмах с заданными условиями.

    :param page_size: число фильмов.
    :param page_number: номер страницы.
    :param sort: сортировка по IMDB рейтингу.
                 `imdb_rating` - по возрастанию, `-imdb_rating` - по убыванию.
    :param genre: жанр, по которому фильмы будут отфильтрованы.
    """
    return await film_service.get_films(
        request_to_str(request),
        page_number=page_number,
        page_size=page_size,
        sort=sort,
        genre=genre,
    )


@router.get("/search/")
async def search_films(
    request: Request,
    query: str,
    page_number: int = Query(0, ge=0),
    page_size: int = Query(50, ge=0),
    film_service: FilmService = Depends(get_film_service),
) -> list[FilmWork]:
    """
    :param query:
    :param page_size:
    :param page_number:
    :param film_service:
    """
    return await film_service.search_films(
        request_to_str(request),
        query=query,
        page_number=page_number,
        page_size=page_size,
    )
