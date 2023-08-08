import requests


def get_headhunter_request(employer_id: str) -> dict:
    """
    Функция делает запрос к HeadHunter через url запрос, возвращает словарь вакансий работадателя по переданному в юрл айди
    :param employer_id: айди работодателя
    :return: словарь с вакансиями
    """
    response = requests.get('https://api.hh.ru/vacancies?employer_id=%s' % employer_id)
    response_json = response.json()
    return response_json

#
# print(get_headhunter_request('1060266'))
