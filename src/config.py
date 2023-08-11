from configparser import ConfigParser


def config(filename: str, section='postgres') -> dict:
    parser = ConfigParser()
    parser.read(filename)
    database = {}

    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            database[param[0]] = param[1]
    else:
        raise Exception('Section {0} is not founded in the {1} file.'.format(section, filename))

    return database
