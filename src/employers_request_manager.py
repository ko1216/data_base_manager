from src.request_funcs import get_headhunter_request


class EmployersRequestManager:
    all_vacancies = []

    def __init__(self, filename: str):
        self.filename = filename

    def read_file(self) -> dict[str, str]:
        """
        Метод обращается к записанному файлу, в котором указаны названия компаний и их айди на Headhunter,
        читает строки файла и возвращает словарь с названиями компаний и их айди
        :return: словарь
        """
        employers = {}

        with open(self.filename, encoding='utf-8') as f:
            content = f.readlines()
            for line in content:
                employer = line.strip().split('=')
                employers[employer[0]] = employer[-1]

        return employers

    def vacancies_writer(self) -> None:
        """
        Метод делает запросы через API HeadHunter на сайт для получения информации о вакансиях работадателей по их id
        После этого передает информацию о всех вакансиях работадателей из списка в общий список - атрибут класса
        """
        self.all_vacancies.clear()

        for employer_id in self.read_file().values():
            vacancies = get_headhunter_request(employer_id)['items']
            self.all_vacancies.extend(vacancies)

