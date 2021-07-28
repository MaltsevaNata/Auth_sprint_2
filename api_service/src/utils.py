from fastapi import Request
from furl import furl


def request_to_str(request: Request) -> str:
    """
    Преобразует request в строку с параметрами запроса, исключая base_url.

    То есть, запрос:
    http://smth.com/auth/v1/film/?page_number=0&page_size=50&sort=imdb_rating,
    будет преобразован в /auth/v1/film/?page_number=0&page_size=50&sort=imdb_rating
    """
    pathstr = furl(request.url).pathstr
    return furl(pathstr, query_params=request.query_params).tostr()
