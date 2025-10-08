from datetime import datetime

from yacut import db
import string
import random


class URLMap(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    original = db.Column(db.String(256), unique=True, nullable=False)
    short = db.Column(db.String(64), unique=True, nullable=False)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    def to_dict(self):
        return {
            'url': self.original,
            'short_link': f'http://localhost/{self.short}'
        }

    @classmethod
    def get_by_short_id(cls, short_id):
        return cls.query.filter_by(short=short_id).first()

    @classmethod
    def add_url_map(cls, original_url, custom_id=None):
        from .error_handlers import ShortExistsException

        if custom_id:
            if custom_id == 'files':
                raise ShortExistsException('Предложенный вариант короткой ссылки уже существует.')

            if len(custom_id) > 16:
                raise ShortExistsException('Указано недопустимое имя для короткой ссылки')

            allowed_chars = string.ascii_letters + string.digits
            if not all(c in allowed_chars for c in custom_id):
                raise ShortExistsException('Указано недопустимое имя для короткой ссылки')

            if cls.get_by_short_id(custom_id):
                raise ShortExistsException('Предложенный вариант короткой ссылки уже существует.')

            short_id = custom_id
        else:
            short_id = cls.generate_short_id()

        url_map = cls(original=original_url, short=short_id)
        db.session.add(url_map)
        db.session.commit()
        
        return url_map

    @classmethod
    def generate_short_id(cls):
        chars = string.ascii_letters + string.digits
        while True:
            short_id = ''.join(random.choices(chars, k=6))
            if not cls.get_by_short_id(short_id):
                return short_id
