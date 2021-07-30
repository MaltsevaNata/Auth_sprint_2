import pytest

# Формат параметров: (query_params, expected_data_file, response_status, page_size)

# проверка параметров по умолчанию
default_params = [({}, "film_list_default.json", 200, 50)]

sort_params = [
    # сортировка по возрастанию
    ({"sort": "imdb_rating"}, "film_list_default.json", 200, 50),

    # по убыванию
    ({"sort": "-imdb_rating"}, "film_list_desc_sorted.json", 200, 50),

    # несуществующий вариант сортировки
    ({"sort": "rating"}, None, 422, None)
]


page_num_params = [
    # запрос по номеру страницы
    ({"page_number": 15}, "film_list_page_number_15.json", 200, 50),

    # последняя страница поиска
    ({"page_number": 19}, "film_list_page_number_19.json", 200, 49),

    # неверное значение параметра
    ({"page_number": "two"}, None, 422, None),

    # несуществующая страница
    ({"page_number": 20}, None, 200, 0),

    # отрицательный номер страницы
    ({"page_number": -1}, None, 422, None)
]


page_size_params = [
    # задание кол-ва элементов на странице
    ({"page_size": 99}, "film_list_page_size_99.json", 200, 99),

    # размер страницы больше числа элементов на ней
    ({"page_size": 1000}, "film_list_page_size_1000.json", 200, 999),

    # отрицательный размер страницы
    ({"page_size": -1}, None, 422, None)
]


genre_params = [
    # фильтрация по жанру
    ({"genre": "Documentary"}, "film_list_genre_documentary.json", 200, 50),
    ({"genre": "Reality-TV"}, "film_list_genre_realitytv.json", 200, 38),

    # несуществующий жанр
    ({"genre": "Cartoon"}, None, 200, 0)
]


combined_params = [
    # комбинация всех параметров
    ({"genre": "Action", "page_size": 5, "page_number": 2, "sort": "-imdb_rating"},
     "film_list_combined.json", 200, 5),

    # неверное значение параметра
    ({"genre": "Action", "page_size": 5, "page_number": 2, "sort": "id"}, None, 422, None),

    # запрос к несуществующей странице
    ({"genre": "Comedy", "page_size": 10, "page_number": 100}, None, 200, 0)
]

# Формат параметров: (film_id, expected_data_list, response_status)
film_id_params = [
    # запрос к существующим id
    ('f92c6b11-3f73-4c3f-a9e3-85b1bb91284b',
     "film_id_f92c6b11-3f73-4c3f-a9e3-85b1bb91284b.json", 200),
    ('5a5f31ab-d212-4512-8e2b-23421854508a',
     "film_id_5a5f31ab-d212-4512-8e2b-23421854508a.json", 200),

    # запрос к несуществующему id
    ('c8cb8aa5-926c-4180-81cb-404e2be58a2c', None, 404)
]
