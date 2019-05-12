from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import FlaskAppConfig

app = Flask(__name__)
app.config.from_object(FlaskAppConfig)
db = SQLAlchemy(app)

from app import routes, routes_api_analysis, models