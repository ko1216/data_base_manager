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

    def save_vacancies(self) -> None:
        """
        Метод делает запросы через API HeadHunter на сайт для получения информации о вакансиях работадателей по их id
        После этого передает информацию о всех вакансиях работадателей из списка в общий список - атрибут класса
        """
        self.all_vacancies.clear()
        page = 0
        employers_ids = []
        for id in self.read_file().values():
            employers_ids.append(id)

        params = {'text': 'python',
                  'area': '1',
                  'page': str(page),
                  'per_page': '100',
                  'only_with_salary': True,
                  'employer_id': employers_ids
                  }

        for page in range(0, 20):
            vacancies = get_headhunter_request(params)['items']
            self.all_vacancies += vacancies


# emp = EmployersRequestManager('employers_ids')
# emp.save_vacancies()
# print(emp.all_vacancies)
