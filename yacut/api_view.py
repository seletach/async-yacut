from flask import jsonify, request
from http import HTTPStatus

from settings import Config

from . import app
from .error_handlers import InvalidAPIUsage, ShortExistsException
from .models import URLMap


@app.route('/api/id/', methods=('POST',))
def add_url_map():
    """Создает новую короткую ссылку для указанного URL."""
    data = request.get_json(silent=True)

    if not data:
        raise InvalidAPIUsage(Config.MISSING_REQIEST)

    if 'url' not in data:
        raise InvalidAPIUsage('"url" является обязательным полем!')

    try:
        url_map = URLMap.add_url_map(data.get('url'), data.get('custom_id'))
    except ShortExistsException as e:
        raise InvalidAPIUsage(str(e))

    return jsonify(url_map.to_dict()), HTTPStatus.CREATED


@app.route('/api/id/<short_id>/', methods=('GET',))
def get_original_url(short_id):
    """Возвращает оригинальный URL для указанной короткой ссылки."""
    url_map = URLMap.query.filter_by(short=short_id).first()
    if url_map is None:
        raise InvalidAPIUsage('Указанный id не найден', 404)
    return jsonify({'url': url_map.original}), HTTPStatus.OK
