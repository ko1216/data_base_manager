from abc import ABC
import psycopg2
from src.employers_request_manager import EmployersRequestManager


class DBConnector(ABC):
    def __init__(self, database_name: str, params: dict) -> None:
        super().__init__()
        self.database_name = database_name
        self.params = params


class DBCreator(DBConnector):

    def create_database(self) -> None:
        conn = psycopg2.connect(dbname='postgres', **self.params)
        conn.autocommit = True
        cur = conn.cursor()

        cur.execute(f'DROP DATABASE {self.database_name}')
        cur.execute(f'CREATE DATABASE {self.database_name}')

        cur.close()
        conn.close()

    def create_tables(self) -> None:
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

    def get_companies_and_vacancies_count(self) -> (list[str], dict[str, int]):
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

                # for count in cur.fetchone():
                #     for company in company_names_list:
                #         company_vacancies_amount[company] = count

        return company_names_list, company_vacancies_amount

    def get_all_vacancies(self):
        conn = psycopg2.connect(dbname=self.database_name, **self.params)
        vacancies_list = []

        with conn.cursor() as cur:
            cur.execute('''SELECT vacancies_name, company_name, salary_from, salary_to, url 
                        FROM vacancies''')

            for vacancy in cur.fetchall():
                vacancies_list.append(vacancy)

        return vacancies_list
