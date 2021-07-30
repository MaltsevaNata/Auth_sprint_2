from pathlib import Path

import pytest

from ..testdata.test_parameters.genre_params import (
    default_params,
    genre_id_params
)
from ..utils import conclude_result

parent_dir = Path(__file__).parents[1]
files_dir = parent_dir.joinpath("testdata", "expected_data", "genres")


@pytest.mark.parametrize(
    "query_params, expected_data_file, status, page_size",
    [
        *default_params,
    ],
)
@pytest.mark.usefixtures("clear_cache")
@pytest.mark.asyncio
async def test_genre_list(
        make_get_request,
        query_params: dict,
        expected_data_file: str,
        status: int,
        page_size: int,
):
    """
    Проверка запроса списка жанров
    """
    response = await make_get_request("/genre", query_params)

    conclude_result(response.body, response.status, expected_data_file, status, page_size, files_dir)


@pytest.mark.parametrize("genre_id, expected_data_file, status", [*genre_id_params])
@pytest.mark.usefixtures("clear_cache")
@pytest.mark.asyncio
async def test_genre_by_id(
        make_get_request, genre_id: str, expected_data_file: str, status: int
):
    """
    Проверка поиска фильма по id
    """
    response = await make_get_request(f"""/genre/{genre_id}""", {})

    conclude_result(response.body, response.status, expected_data_file, status, None, files_dir)
