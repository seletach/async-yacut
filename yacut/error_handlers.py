from flask import jsonify, render_template
from http import HTTPStatus

from . import app


class InvalidAPIUsage(Exception):
    """Исключение для обработки ошибок API."""
    status_code = HTTPStatus.BAD_REQUEST

    def __init__(self, message, status_code=None):
        super().__init__()
        self.message = message
        if status_code is not None:
            self.status_code = status_code

    def to_dict(self):
        """Преобразует исключение в словарь для JSON-ответа."""
        return dict(message=self.message)


class ShortExistsException(Exception):
    """Исключение для случая, когда короткая ссылка уже существует."""
    pass


@app.errorhandler(InvalidAPIUsage)
def invalid_api_usage(error):
    """Обрабатывает исключения InvalidAPIUsage и возвращает JSON-ответ."""
    return jsonify(error.to_dict()), error.status_code


@app.errorhandler(ShortExistsException)
def short_exists_error(error):
    """Обрабатывает исключения ShortExistsException и возвращает JSON-ответ."""
    return jsonify({'message': str(error)}), HTTPStatus.BAD_REQUEST


@app.errorhandler(404)
def page_not_found(error):
    """Обрабатывает ошибку 404 и возвращает кастомную страницу."""
    return render_template('404.html'), HTTPStatus.NOT_FOUND


@app.errorhandler(500)
def internal_error(error):
    """Обрабатывает ошибку 500 и возвращает кастомную страницу."""
    return render_template('500.html'), HTTPStatus.INTERNAL_SERVER_ERROR
