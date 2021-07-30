from pathlib import Path

import pytest

from ..utils import conclude_result
from ..testdata.test_parameters.person_params import  (
    person_id_params
)

parent_dir = Path(__file__).parents[1]
files_dir = parent_dir.joinpath("testdata", "expected_data", "persons")


@pytest.mark.parametrize("person_id, expected_data_file, status", [*person_id_params])
@pytest.mark.usefixtures("clear_cache")
@pytest.mark.asyncio
async def test_person_by_id(
    make_get_request, person_id: str, expected_data_file: str, status: int
):
    """
    Проверка поиска фильма по id
    """
    response = await make_get_request(f"""/person/{person_id}""", {})

    conclude_result(response.body, response.status, expected_data_file, status, None, files_dir)