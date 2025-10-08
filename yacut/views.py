from flask import render_template, flash, redirect

from .forms import LinkForm
from .models import URLMap

from . import app, db
import random
import string
import logging

logger = logging.getLogger(__name__)

def get_custom_id():
    available_chars = string.ascii_letters + string.digits

    while True:
        short_link = ""
        for i in range(6):
            random_char = random.choice(available_chars)
            short_link += random_char

        existing_url = URLMap.query.filter_by(short=short_link).first()

        if not existing_url:
            return short_link

@app.route('/', methods=['GET', 'POST'])
def index_view():
    form = LinkForm()

    if form.validate_on_submit():
        original_link = form.original_link.data

        if form.custom_id.data:
            custom_id = form.custom_id.data.strip()
        else:
            custom_id = None

        if hasattr(form, 'existing_short_id'):
            flash('Для этой ссылки уже существует короткий вариант...')
            return render_template('main.html', form=form, short_id=form.existing_short_id)

        if custom_id:
            short_id = custom_id
        else:
            short_id = get_custom_id()

        new_url = URLMap(original=original_link, short=short_id)
        db.session.add(new_url)
        db.session.commit()

        flash('Ссылка успешно укорочена!')

        return render_template('main.html', form=form, short_id=short_id)

    return render_template('main.html', form=form)

@app.route('/<short_id>')
def redirect_view(short_id):
    url_map = URLMap.query.filter_by(short=short_id).first_or_404()
    return redirect(url_map.original)
