from flask_wtf import FlaskForm
from wtforms import URLField, StringField, SubmitField, ValidationError
from wtforms.validators import DataRequired, URL, Length, Optional
from flask_wtf.file import MultipleFileField, FileAllowed

from .models import URLMap


class LinkForm(FlaskForm):
    original_link = URLField('Длинная ссылка',
                             validators=[DataRequired(message='Обязательное поле'),
                                         URL(message='Введите корректный URL адрес')])
    custom_id = StringField('Ваш вариант короткой ссылки',
                            validators=[Length(1, 16), Optional()])
    submit = SubmitField('Укоротить')

    def validate_custom_id(self, field):
        if field.data and field.data.strip():
            custom_id = field.data.strip()
            if custom_id == 'files':
                raise ValidationError('Предложенный вариант короткой ссылки уже существует.')
            
            existing_url = URLMap.query.filter_by(short=custom_id).first()
            if existing_url:
                raise ValidationError('Предложенный вариант короткой ссылки уже существует.')

    def validate_original_link(self, field):
        """Валидация для проверки существующей оригинальной ссылки"""
        if field.data:
            existing_original = URLMap.query.filter_by(original=field.data).first()
            if existing_original:
                self.existing_short_id = existing_original.short
                raise ValidationError('Для этой ссылки уже существует короткий вариант.')


class UploadForm(FlaskForm):
    files = MultipleFileField(
        'Выберите файлы для загрузки')
    submit = SubmitField('Загрузить на Яндекс Диск')
