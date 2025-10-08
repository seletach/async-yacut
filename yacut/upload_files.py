from flask import render_template, request, flash, url_for
import requests
import os

from . import app
from .forms import UploadForm
from .models import URLMap

API_HOST = 'https://cloud-api.yandex.net/'
API_VERSION = 'v1'
REQUEST_UPLOAD_URL = f'{API_HOST}{API_VERSION}/disk/resources/upload'
DOWNLOAD_LINK_URL = f'{API_HOST}{API_VERSION}/disk/resources/download'

DISK_TOKEN = os.environ.get('DISK_TOKEN')
AUTH_HEADERS = {'Authorization': f'OAuth {DISK_TOKEN}'}


def upload_file_to_yandex_disk(file,
                               remote_folder='disk:/Приложения/YaCut/'):
    filename = file.filename
    remote_path = f'{remote_folder}{filename}'

    payload = {'path': remote_path, 'overwrite': 'true'}
    response = requests.get(
        REQUEST_UPLOAD_URL,
        headers=AUTH_HEADERS,
        params=payload
    )
    response.raise_for_status()
    upload_url = response.json()['href']

    response = requests.put(upload_url, data=file.read())
    response.raise_for_status()

    response = requests.get(
        DOWNLOAD_LINK_URL,
        headers=AUTH_HEADERS,
        params={'path': remote_path}
    )
    response.raise_for_status()
    download_url = response.json()['href']

    return {
        'filename': filename,
        'remote_path': remote_path,
        'download_url': download_url
    }


def create_short_link_for_file(download_url, filename):
    url_map = URLMap.add_url_map(download_url)
    return {
        'filename': filename,
        'short_link': url_for('redirect_view',
                              short_id=url_map.short,
                              _external=True),
        'original_url': download_url
    }


@app.route('/files', methods=['GET', 'POST'])
def upload_files():
    form = UploadForm()

    if form.validate_on_submit():
        valid_files = []
        if form.files.data:
            for f in form.files.data:
                if f and f.filename and f.filename.strip():
                    valid_files.append(f)

        if not valid_files:
            flash('Выберите хотя бы один файл для загрузки')
            return render_template('upload_files.html', form=form)

        try:
            file_links = []
            for file in valid_files:
                if file.filename:
                    uploaded_file = upload_file_to_yandex_disk(file)

                    short_link_info = create_short_link_for_file(
                        uploaded_file['download_url'],
                        uploaded_file['filename']
                    )
                    file_links.append(short_link_info)

            if file_links:
                form.file_links = file_links
                return render_template(
                    'upload_files.html',
                    form=form,
                    file_links=file_links
                )
            else:
                flash('Не удалось загрузить файлы')

        except Exception as e:
            flash(f'Ошибка при загрузке файлов: {str(e)}')

    return render_template('upload_files.html', form=form)
