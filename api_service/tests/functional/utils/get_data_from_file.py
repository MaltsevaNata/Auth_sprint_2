import json
from typing import Union


def get_data_from_file(files_dir, expected_data_file: str) -> Union[list, dict]:
    file = files_dir.joinpath(expected_data_file)
    with open(file, encoding="utf-8") as json_file:
        data = json.load(json_file)
    return data
