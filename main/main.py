from src.config import config
from src.employers_request_manager import EmployersRequestManager
from src.database_classes import DBCreator, DBManager

import os

employers_ids_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'src/employers_ids')
database_ini_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'src/database.ini')
params = config(database_ini_path)


def main():
    print('''Приветстую Вас в программе, которая создает базу данных в PostreSQL, наполняет данными вакансий
от работодателей из файла 'employers_ids', а также фильтрует полученные вакансии и выводит их в консоль.''')

    employers_request_manager = EmployersRequestManager(employers_ids_path)
    employers_request_manager.save_vacancies()

    db_name = str(input('Введите название для базы данных: '))
    database = DBCreator(db_name, params)
    database.create_database()
    database.create_tables()
    database.insert_tables(employers_ids_path)
    print(f'База данных {db_name} создана и наполнена данными')

    manager = DBManager(db_name, params)
    companies_and_vacancies_count = manager.get_companies_and_vacancies_count()

    print(f'\nСписок компаний, по которым была сделана выборка и которые занесены в таблицу:')
    for company in companies_and_vacancies_count[0]:
        print(company)

    print('\nКол-во вакансий у каждой компании согласно результатам запроса (ограничение по городу Москве)')
    for employer, vacancies_count in companies_and_vacancies_count[1].items():
        print(f'{employer}: {vacancies_count} вакансий')

    all_vacancies = manager.get_all_vacancies()
    DBManager.get_results_vacancies(all_vacancies, 'all')

    print(manager.get_avg_salary())

    vacancies_with_higher_salary = manager.get_vacancies_with_higher_salary()
    DBManager.get_results_vacancies(vacancies_with_higher_salary, 'higher_salary')

    user_keyword = str(input('''Введите ключевое слово, которое могло бы соответствовать вакансии или одному из навыков
    этой вакансии: '''))
    user_choice = manager.get_vacancies_with_keyword(user_keyword)
    DBManager.get_results_vacancies(user_choice, 'keyword')


if __name__ == '__main__':
    main()
