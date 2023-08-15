from abc import ABC
import psycopg2
from src.employers_request_manager import EmployersRequestManager


class DBConnector(ABC):
    def __init__(self, database_name: str, params: dict) -> None:
        super().__init__()
        self.database_name = database_name
        self.params = params


class DBCreator(DBConnector):
    """
    Класс для создания БД, создания таблиц и заполнения их данными
    """

    def create_database(self) -> None:
        """
        Метод подключается к локальной БД postgres и создает в ней БД с названием, которое передается в экземпляр каласа
        при инициализации
        """
        conn = psycopg2.connect(dbname='postgres', **self.params)
        conn.autocommit = True
        cur = conn.cursor()

        try:
            cur.execute(f'DROP DATABASE {self.database_name}')
        except psycopg2.Error:
            cur.execute(f'CREATE DATABASE {self.database_name}')
        else:
            cur.execute(f'CREATE DATABASE {self.database_name}')

        cur.close()
        conn.close()

    def create_tables(self) -> None:
        """
        Метод подключается к созданной БД и спомощью sql запрсоов задает параметры для двух создаваемых таблиц:
        employers, vacancies
        :return:
        """
        conn = psycopg2.connect(dbname=self.database_name, **self.params)

        with conn.cursor() as cur:
            cur.execute('''
                    CREATE TABLE employers (
                        employer_id SERIAL PRIMARY KEY,
                        name VARCHAR(255) NOT NULL,
                        url TEXT
                        )
            ''')

        with conn.cursor() as cur:
            cur.execute('''
                    CREATE TABLE vacancies (
                        vacancies_id SERIAL PRIMARY KEY,
                        employer_id INT,
                        vacancies_name VARCHAR(255) NOT NULL,
                        company_name VARCHAR(255) NOT NULL,
                        salary_from INT,
                        salary_to INT,
                        requirement VARCHAR,
                        url TEXT,
                        CONSTRAINT vacancies_fk
                        FOREIGN KEY (employer_id) REFERENCES employers (employer_id)
                        )
            ''')

        conn.commit()
        conn.close()

    def insert_tables(self, employers_ids_filename) -> None:
        """
        Этот метод с помощью реализованного класса EmployerRequestManager парсит полученные с помощью запроса вакансии и
        вставляет их в подготовленные поля таблиц
        :param employers_ids_filename: путь к файлу, в котором находится первичный список с работодателями и их айди
        """
        employers = EmployersRequestManager(employers_ids_filename)
        employers.save_vacancies()
        emp_dict = employers.read_file()

        conn = psycopg2.connect(dbname=self.database_name, **self.params)

        with conn.cursor() as cur:
            for k, v in emp_dict.items():
                cur.execute(f'''
                        INSERT INTO employers (name, url)
                        VALUES ('{k}', 'https://hh.ru/employer/{v}')
                ''')

        with conn.cursor() as cur:
            emp_dict_with_pos = {}
            pos = 0
            for key in emp_dict.keys():
                pos += 1
                emp_dict_with_pos[key] = pos

            for vacancy in employers.all_vacancies:
                if vacancy['employer']['name'] in emp_dict_with_pos.keys():
                    employer_id = emp_dict_with_pos[vacancy['employer']['name']]
                    cur.execute(f'''
                        INSERT INTO vacancies (employer_id, vacancies_name, company_name, salary_from, salary_to, 
                        requirement, url)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)''', (employer_id,
                                                                 vacancy['name'],
                                                                 vacancy['employer']['name'],
                                                                 vacancy['salary']['from'],
                                                                 vacancy['salary']['to'],
                                                                 vacancy['snippet']['requirement'],
                                                                 vacancy['apply_alternate_url']),
                                )

        conn.commit()
        conn.close()


class DBManager(DBConnector):
    """
    Класс для подключения к таблицами и фильтрации данных
    """

    def get_companies_and_vacancies_count(self) -> tuple[list[str], dict[str, int]]:
        """
        Метод обращается к таблицам employers, vacancies и получает список всех работодателей и словарь, в котором
        каждому работодателю присвоено числовое значение - кол-во вакансий
        :return: tuple[list, dict]
        """
        conn = psycopg2.connect(dbname=self.database_name, **self.params)
        company_names_list = []
        company_vacancies_amount = {}

        with conn.cursor() as cur:
            cur.execute('SELECT * FROM employers')

            for company in cur.fetchall():
                company_names_list.append(company[1])

        with conn.cursor() as cur:
            for name in company_names_list:
                cur.execute(f'''SELECT COUNT(*) FROM vacancies WHERE company_name = '{name}';''')
                company_vacancies_amount[name] = cur.fetchone()[0]

        return company_names_list, company_vacancies_amount

    def get_all_vacancies(self) -> list[tuple]:
        """
        Метод обращается к таблице vacancies и возвращает список всех вакансий по заданным полям
        :return: список вакансий
        """
        conn = psycopg2.connect(dbname=self.database_name, **self.params)
        vacancies_list = []

        with conn.cursor() as cur:
            cur.execute('''SELECT vacancies_name, company_name, salary_from, salary_to, url 
                        FROM vacancies''')

            for vacancy in cur.fetchall():
                vacancies_list.append(vacancy)

        return vacancies_list

    def get_avg_salary(self) -> str:
        """
        Метод получает среднюю сумму заработной платы для всех вакансий всех работодателей
        :return: str
        """
        conn = psycopg2.connect(dbname=self.database_name, **self.params)

        with conn.cursor() as cur:
            cur.execute('''SELECT (AVG(salary_from) + AVG(salary_to)) / 2 
            FROM vacancies''')
            avg_salary = round(cur.fetchone()[0], 2)

        return f'Средняя зарплата всех вакнсий составляет {avg_salary} RUB'

    def get_vacancies_with_higher_salary(self) -> list[tuple]:
        """
        Метод обращается к таблице vacancies и получает список всех вакансий, где зарплата вакансии выше средней ЗП по
        всем вакансиям
        :return: список вакансий
        """
        conn = psycopg2.connect(dbname=self.database_name, **self.params)
        vacancies_with_higher_salary_list = []

        with conn.cursor() as cur:
            cur.execute('''SELECT vacancies_name, company_name, salary_from, salary_to, url 
                        FROM vacancies
                        WHERE (salary_from + salary_to) / 2 > (SELECT (AVG(salary_from) + AVG(salary_to)) / 2 
                        FROM vacancies);''')

            for vacancy in cur.fetchall():
                vacancies_with_higher_salary_list.append(vacancy)

        return vacancies_with_higher_salary_list

    def get_vacancies_with_keyword(self, keyword: str) -> list:
        """
        Метод по ключевому слову ищет в таблице vacancies по столбцам(полям) vacancies_name, requirement подходящие
        вакансии
        :param keyword: str
        :return: список вакансий
        """
        conn = psycopg2.connect(dbname=self.database_name, **self.params)
        vacancies_with_keyword_list = []

        with conn.cursor() as cur:
            cur.execute(f'''SELECT vacancies_name, company_name, salary_from, salary_to, url
                            FROM vacancies
                            WHERE LOWER(vacancies_name) LIKE '%{keyword}%' OR LOWER(requirement) LIKE '%{keyword}%';''')

            for vacancy in cur.fetchall():
                vacancies_with_keyword_list.append(vacancy)

        return vacancies_with_keyword_list

    @staticmethod
    def get_results_vacancies(vacancies_list: list, codeword: str):
        if len(vacancies_list) == 0:
            print('Нет вакансий соответствуйющих вашему запросу')
        else:
            if codeword == 'all':
                print('''\n Ниже представлены все вакансии из таблицы vacancies в формате:
Название вакансии
Название компании
Зарплата от (если указана)
Зарплата до (если указана)
Ссылка на вакансию''')
            elif codeword == 'higher_salary':
                print('''\n Ниже представлены вакансии из таблицы vacancies, зарплата которых выше средней ЗП всех вакансий в 
таблице:
Название вакансии
Название компании
Зарплата от (если указана)
Зарплата до (если указана)
Ссылка на вакансию''')
            elif codeword == 'keyword':
                print('''\n Ниже представлены вакансии из таблицы vacancies, в которых нашлось соответствие ключевому слову:
Название вакансии
Название компании
Зарплата от (если указана)
Зарплата до (если указана)
Ссылка на вакансию''')

            for vacancy in vacancies_list:
                print('')
                for vacancies_character in vacancy:
                    print(vacancies_character)
