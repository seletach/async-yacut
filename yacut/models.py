import random
import string
import re
from datetime import datetime

from flask import url_for

from settings import Config
from yacut import db

from .error_handlers import ShortExistsException


class URLMap(db.Model):
    """Модель для хранения соответствия оригинальных и коротких ссылок."""
    id = db.Column(db.Integer, primary_key=True)
    original = db.Column(db.String(256), unique=True, nullable=False)
    short = db.Column(db.String(64), unique=True, nullable=False)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    def to_dict(self):
        """Преобразует объект в словарь для API-ответа."""
        return {
            'url': self.original,
            'short_link': url_for('redirect_view',
                                  short_id=self.short,
                                  _external=True)
        }

    @classmethod
    def get_by_short_id(cls, short_id):
        """Возвращает объект URLMap по короткому идентификатору."""
        return cls.query.filter_by(short=short_id).first()

    @classmethod
    def add_url_map(cls, original_url, custom_id=None):
        """Создает новую запись соответствия URL и короткой ссылки."""
        if custom_id:
            if custom_id == 'files':
                raise ShortExistsException(Config.VALIDATE_SHRT_MSG)

            if len(custom_id) > 16:
                raise ShortExistsException(Config.WRONG_NAME)

            if not re.match(r'^[A-Za-z0-9]+$', custom_id):
                raise ShortExistsException(Config.WRONG_NAME)

            if cls.get_by_short_id(custom_id):
                raise ShortExistsException(Config.VALIDATE_SHRT_MSG)

            short_id = custom_id
        else:
            short_id = cls.generate_short_id()

        url_map = cls(original=original_url, short=short_id)
        db.session.add(url_map)
        db.session.commit()

        return url_map

    @classmethod
    def generate_short_id(cls):
        """Генерирует уникальный короткий идентификатор."""
        chars = string.ascii_letters + string.digits
        while True:
            short_id = ''.join(random.choices(chars,
                                              k=Config.LENGHT_ID))
            if not cls.get_by_short_id(short_id):
                return short_id
