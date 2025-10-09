import logging

from flask import render_template, flash, redirect

from . import app, db
from .forms import LinkForm
from .models import URLMap
from settings import Config

logger = logging.getLogger(__name__)


@app.route('/', methods=['GET', 'POST'])
def index_view():
    """Главная страница для создания коротких ссылок."""
    form = LinkForm()

    if form.validate_on_submit():
        original_link = form.original_link.data

        if form.custom_id.data:
            custom_id = form.custom_id.data.strip()
        else:
            custom_id = None

        if hasattr(form, 'existing_short_id'):
            flash(Config.AVAILABILITY_SHORT)
            return render_template('main.html',
                                   form=form,
                                   short_id=form.existing_short_id)

        if custom_id:
            short_id = custom_id
        else:
            short_id = URLMap.generate_short_id()

        new_url = URLMap(original=original_link, short=short_id)
        db.session.add(new_url)
        db.session.commit()

        flash('Ссылка успешно укорочена!')

        return render_template('main.html', form=form, short_id=short_id)

    return render_template('main.html', form=form)


@app.route('/<short_id>', endpoint='redirect_view')
def redirect_view(short_id):
    """Перенаправляет с короткой ссылки на оригинальный URL."""
    url_map = URLMap.query.filter_by(short=short_id).first_or_404()
    return redirect(url_map.original)
