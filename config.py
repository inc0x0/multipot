import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    ANALYSIS_TOKEN = 'verysecret'

    EXCLUDE_FROM_LOGGING = ['/analysis/index',
                            '/analysis/details',
                            '/analysis/wordpress',
                            '/api/analysis',
                            '/static/assets',
                            '/favicon.ico']


class FlaskAppConfig(object):
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
