from src.config import config
from src.employers_request_manager import EmployersRequestManager
from src.database_classes import DBCreator

import os

employers_ids_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'src/employers_ids')
database_ini_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'src/database.ini')
params = config(database_ini_path)


def main():
    employers_request_manager = EmployersRequestManager(employers_ids_path)
    employers_request_manager.vacancies_writer()
    vacancies = employers_request_manager.all_vacancies

    database = DBCreator('hh_vacancies', params)
    database.create_database()
    database.create_tables()


if __name__ == '__main__':
    main()
