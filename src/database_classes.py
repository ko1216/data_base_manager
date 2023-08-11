from abc import ABC
import psycopg2


class DBConnector(ABC):
    def __init__(self) -> None:
        pass


class DBCreator(DBConnector):
    def __init__(self, database_name: str, params: dict) -> None:
        super().__init__()
        self.database_name = database_name
        self.params = params

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
                        employer_id INT REFERENCES employers(employer_id),
                        vacancies_name VARCHAR(255) NOT NULL,
                        salary_from INT,
                        salary_to INT,
                        city VARCHAR(255),
                        about_vacancy VARCHAR,
                        url TEXT
                        )
            ''')

        conn.commit()
        conn.close()

    def insert_tables(self) -> None:
        pass