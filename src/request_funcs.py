import requests


def get_headhunter_request(url_params=None) -> dict:
    """
    Функция делает запрос к HeadHunter через url запрос, возвращает словарь вакансий работадателя по переданному в юрл айди
    :param url_params: параметры запроса
    :return: словарь с вакансиями
    """
    response = requests.get('https://api.hh.ru/vacancies', params=url_params)
    response_json = response.json()
    return response_json


# print(get_headhunter_request('1060266'))
