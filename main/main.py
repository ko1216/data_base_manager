from src.employers_request_manager import EmployersRequestManager

import os

path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'src/employers_ids')


def main():
    employers_request_manager = EmployersRequestManager(path)
    employers_request_manager.vacancies_writer()
    vacancies = employers_request_manager.all_vacancies

    DBCreator()


if __name__ == '__main__':
    main()
