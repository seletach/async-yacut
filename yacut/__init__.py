from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from settings import Config

app=Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)

from yacut import (views,
                   api_view,
                   error_handlers,
                   forms,
                   models,
                   upload_files)
