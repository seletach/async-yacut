
import os
import asyncio
import aiohttp

from flask import render_template, flash, url_for

from . import app
from .forms import UploadForm
from .models import URLMap

API_HOST = 'https://cloud-api.yandex.net/'
API_VERSION = 'v1'
REQUEST_UPLOAD_URL = f'{API_HOST}{API_VERSION}/disk/resources/upload'
DOWNLOAD_LINK_URL = f'{API_HOST}{API_VERSION}/disk/resources/download'

DISK_TOKEN = os.environ.get('DISK_TOKEN')
AUTH_HEADERS = {'Authorization': f'OAuth {DISK_TOKEN}'}


async def upload_file_to_yandex_disk(session,
                                     file,
                                     remote_folder='disk:/Приложения/YaCut/'):
    """
    Асинхронно загружает файл на Диск и возвращает информацию о загрузке.
    """
    filename = file.filename
    remote_path = f'{remote_folder}{filename}'

    async with session.get(
        REQUEST_UPLOAD_URL,
        headers=AUTH_HEADERS,
        params={'path': remote_path, 'overwrite': 'true'}
    ) as response:
        response.raise_for_status()
        upload_data = await response.json()
        upload_url = upload_data['href']

    file_data = file.read()
    async with session.put(upload_url, data=file_data) as response:
        response.raise_for_status()

    async with session.get(
        DOWNLOAD_LINK_URL,
        headers=AUTH_HEADERS,
        params={'path': remote_path}
    ) as response:
        response.raise_for_status()
        download_data = await response.json()
        download_url = download_data['href']

    return {
        'filename': filename,
        'remote_path': remote_path,
        'download_url': download_url
    }


async def upload_files_async(files):
    """Асинхронно загружает несколько файлов на Яндекс Диск."""
    async with aiohttp.ClientSession() as session:
        tasks = []
        for file in files:
            if file and file.filename and file.filename.strip():
                task = upload_file_to_yandex_disk(session, file)
                tasks.append(task)

        if not tasks:
            return []

        return await asyncio.gather(*tasks, return_exceptions=True)


def get_valid_files(form_files):
    """Извлекает валидные файлы из формы."""
    if not form_files:
        return []

    valid_files = []

    for file in form_files:
        if file and file.filename and file.filename.strip():
            valid_files.append(file)

    return valid_files


def process_upload_results(upload_results, valid_files):
    """Обрабатывает результаты загрузки файлов."""
    file_links = []
    errors = []

    for i, result in enumerate(upload_results):
        if isinstance(result, Exception):

            if i < len(valid_files):
                filename = valid_files[i].filename
            else:
                filename = 'Неизвестный файл'
            errors.append(f'Ошибка при загрузке {filename}: {str(result)}')

        else:
            short_link_info = create_short_link_for_file(
                result['download_url'],
                result['filename']
            )
            file_links.append(short_link_info)

    return file_links, errors


def create_short_link_for_file(download_url, filename):
    """Создает короткую ссылку для загруженного файла."""
    url_map = URLMap.add_url_map(download_url)
    return {
        'filename': filename,
        'short_link': url_for('redirect_view',
                              short_id=url_map.short,
                              _external=True),
        'original_url': download_url
    }


def run_async_upload(files):
    """Запускает асинхронную загрузку файлов."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(upload_files_async(files))
    finally:
        loop.close()


@app.route('/files', methods=['GET', 'POST'])
def upload_files():
    """
    Обрабатывает загрузку файлов на Яндекс Диск и создание коротких ссылок.
    """
    form = UploadForm()

    if not form.validate_on_submit():
        return render_template('upload_files.html', form=form)

    valid_files = get_valid_files(form.files.data)
    if not valid_files:
        flash('Выберите хотя бы один файл для загрузки')
        return render_template('upload_files.html', form=form)

    try:
        upload_results = run_async_upload(valid_files)
        file_links, errors = process_upload_results(upload_results,
                                                    valid_files)

        for error in errors:
            flash(error)

        if file_links:
            return render_template(
                'upload_files.html',
                form=form,
                file_links=file_links
            )
        elif not errors:
            flash('Не удалось загрузить файлы')

    except Exception as e:
        flash(f'Ошибка при загрузке файлов: {str(e)}')

    return render_template('upload_files.html', form=form)
