# Формат параметров: (genre_id, expected_data_list, response_status)
person_id_params = [
    # запрос к существующим id
    ('f52ed150-be42-4b6d-b6b7-397018b4a6f4', "person_id_f52ed150-be42-4b6d-b6b7-397018b4a6f4.json", 200),
    ('338d3c7e-e089-4287-ac13-d5a403f28bc6', "person_id_338d3c7e-e089-4287-ac13-d5a403f28bc6.json", 200),
    # запрос к несуществующему id
    ('24e98779-ef9e-47da-a018-39435c3997d4', None, 404)
]