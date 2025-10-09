import os


class Config(object):
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URI')
    SECRET_KEY = os.getenv('SECRET_KEY')
    YANDEX_DISK_TOKEN = os.getenv('DISK_TOKEN')
    VALIDATE_SHRT_MSG = 'Предложенный вариант короткой ссылки уже существует.'
    WRONG_NAME = 'Указано недопустимое имя для короткой ссылки'
    AVAILABILITY_SHORT = 'Для этой ссылки уже существует короткий вариант.'
    MISSING_REQIEST = 'Отсутствует тело запроса'
    LENGHT_ID = 6
