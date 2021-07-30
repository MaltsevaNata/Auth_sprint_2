from typing import Optional, Union

from . import get_data_from_file


def conclude_result(body: Optional[Union[list, dict]],
                    status: int,
                    expected_data_file: Optional[str],
                    expected_status: int,
                    expected_page_size: Optional[int],
                    files_dir: Optional[str]):
    # Проверка статуса ответа
    assert status == expected_status

    # Проверка соответствия количества элементов
    if expected_page_size is not None:
        assert len(body) == expected_page_size

    # Проверка соответствия ответа содержимому файла
    if expected_data_file is not None:
        expected_data = get_data_from_file(files_dir, expected_data_file)
        assert body == expected_data


