# Формат параметров: (query_params, expected_data_file, response_status, page_size)

# проверка параметров по умолчанию
default_params = [({}, "genre_list_default.json", 200, 10)]

# Формат параметров: (genre_id, expected_data_list, response_status)
genre_id_params = [
    # запрос к существующим id
    ('c8cb8aa5-926c-4180-81cb-404e2be58a2c', "genre_id_c8cb8aa5-926c-4180-81cb-404e2be58a2c.json", 200),
    ('7a75da54-362e-474d-a7c6-736fd0746f27', "genre_id_7a75da54-362e-474d-a7c6-736fd0746f27.json", 200),
    # запрос к несуществующему id
    ('7c963643-812b-4ca3-9800-ab330ca4a05d', None, 404)
]