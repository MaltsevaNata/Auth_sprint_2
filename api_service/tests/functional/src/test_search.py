import operator
from pathlib import Path

import pytest

from ..testdata.test_parameters.search_params import film_search_params, person_search_params
from ..utils import conclude_result

parent_dir = Path(__file__).parents[1]
files_dir = parent_dir.joinpath("testdata", "expected_data", "search")


@pytest.mark.parametrize(
    "model, query, expected_data_file, status, page_size",
    [
        *film_search_params,
        *person_search_params
    ]
)
@pytest.mark.usefixtures("clear_cache")
@pytest.mark.asyncio
async def test_search(
        make_get_request,
        model: str,
        query: dict,
        expected_data_file: str,
        status: int,
        page_size: int,
):
    """
    Проверка запросов поиска для всех моделей
    """
    response = await make_get_request(f"""/{model}/search/""", query)
    body = sort_by_id(response.body)

    conclude_result(body, response.status, expected_data_file, status, page_size, files_dir)


def sort_by_id(items):
    try:
        sorted_result = sorted(items, key=operator.itemgetter("id"))
        return sorted_result
    except TypeError:  # Ответ не является списком сущностей, а содержит описание ошибки
        return items
