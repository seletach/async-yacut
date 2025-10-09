import re

from flask_wtf import FlaskForm
from flask_wtf.file import MultipleFileField
from wtforms import URLField, StringField, SubmitField, ValidationError
from wtforms.validators import DataRequired, URL, Length, Optional

from settings import Config
from .models import URLMap


class LinkForm(FlaskForm):
    """Форма для создания коротких ссылок."""
    original_link = URLField(
        'Длинная ссылка',
        validators=[DataRequired(message='Обязательное поле'),
                    URL(message='Введите корректный URL адрес')])
    custom_id = StringField('Ваш вариант короткой ссылки',
                            validators=[Length(max=16), Optional()])
    submit = SubmitField('Укоротить')

    def validate_custom_id(self, field):
        """Проверяет валидность пользовательского короткого идентификатора."""
        if field.data and field.data.strip():
            custom_id = field.data.strip()

            if custom_id == 'files':
                raise ValidationError(Config.VALIDATE_SHRT_MSG)

            if not re.match(r'^[A-Za-z0-9]+$', custom_id):
                raise ValidationError(Config.WRONG_NAME)

            existing_url = URLMap.query.filter_by(short=custom_id).first()
            if existing_url:
                raise ValidationError(Config.VALIDATE_SHRT_MSG)

    def validate_original_link(self, field):
        """Проверяет, существует ли уже короткая ссылка для данного URL."""
        if field.data:
            existing_original = URLMap.query.filter_by(
                original=field.data).first()
            if existing_original:
                self.existing_short_id = existing_original.short
                raise ValidationError(Config.AVAILABILITY_SHORT)


class UploadForm(FlaskForm):
    """Форма для загрузки файлов на Яндекс Диск."""
    files = MultipleFileField(
        'Выберите файлы для загрузки')
    submit = SubmitField('Загрузить на Яндекс Диск')
