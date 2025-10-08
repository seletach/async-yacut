from flask_wtf import FlaskForm
from wtforms import (URLField,
                     StringField,
                     SubmitField,
                     ValidationError)
from wtforms.validators import (DataRequired,
                                URL,
                                Length,
                                Optional)
from flask_wtf.file import MultipleFileField

from .models import URLMap
from settings import Config


class LinkForm(FlaskForm):
    original_link = URLField(
        'Длинная ссылка',
        validators=[DataRequired(message='Обязательное поле'),
                    URL(message='Введите корректный URL адрес')])
    custom_id = StringField('Ваш вариант короткой ссылки',
                            validators=[Length(1, 16), Optional()])
    submit = SubmitField('Укоротить')

    def validate_custom_id(self, field):
        if field.data and field.data.strip():
            custom_id = field.data.strip()
            if custom_id == 'files':
                raise ValidationError(Config.VALIDATE_SHRT_MSG)

            existing_url = URLMap.query.filter_by(short=custom_id).first()
            if existing_url:
                raise ValidationError(Config.VALIDATE_SHRT_MSG)

    def validate_original_link(self, field):
        if field.data:
            existing_original = URLMap.query.filter_by(
                original=field.data).first()
            if existing_original:
                self.existing_short_id = existing_original.short
                raise ValidationError(Config.AVAILABILITY_SHORT)


class UploadForm(FlaskForm):
    files = MultipleFileField(
        'Выберите файлы для загрузки')
    submit = SubmitField('Загрузить на Яндекс Диск')
