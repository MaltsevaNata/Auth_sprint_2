import pytest

# Формат параметров: model, query_params, expected_data, status, page_size

film_search_params = [
    # совпадения по заголовку фильма и описанию с параметрами страницы
    ("film", {"query": "captain"}, "query_captain.json", 200, 34),
    ("film", {"query": "star", "page_size": 10, "page_number": 1},
     "query_star_page_1_size_10.json", 200, 10),

    # запрос к несуществующим страницам
    ("film", {"query": "star", "page_size": 10, "page_number": 100}, None, 200, 0),

    # отрицательный номер страницы
    ("film", {"query": "star", "page_number": -1}, None, 422, None),

    # поиск по нескольким словам
    ("film", {"query": "Captain James T. Kirk", "page_size": 100}, "query_Captain_James_size_1000.json",
     200, 46)
]

person_search_params = [
    # совпадения по имени с параметрами страницы
    ("person", {"query": "Jack"}, "query_jack.json", 200, 19),
    ("person", {"query": "Jack", "page_size": 2, "page_number": 3}, "query_jack_page_3_page_size_2.json", 200, 2),

    # поиск по нескольким словам
    ("person", {"query": "Robert Woods", "page_number": 1}, "query_robert_woods_page_1.json", 200, 6),

    # запрос к несуществующим страницам
    ("person", {"query": "Robert Woods", "page_number": 2}, None, 200, 0),

    # отрицательный номер страницы
    ("person", {"query": "Jack", "page_number": -1}, None, 422, None),
]


