import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    MONGODB_DB = '********'
    MONGODB_HOST = '*********'
    MONGODB_PORT = 10058
    MONGODB_USERNAME = '********'
    MONGODB_PASSWORD = '********'
    SECRET_KEY = '**********'
    @staticmethod
    def init_app(app):
        pass

class ProductionConfig(Config):
    @classmethod
    def init_app(cls, app):
        Config.init_app(app)

class DevelopmentConfig(Config):
    DEBUG = True

class HerokuConfig(ProductionConfig):
    @classmethod
    def init_app(cls, app):
        ProductionConfig.init_app(app)
        from werkzeug.contrib.fixers import ProxyFix
        app.wsgi_app = ProxyFix(app.wsgi_app)

        # log to stderr
        import logging
        from logging import StreamHandler
        file_handler = StreamHandler()
        file_handler.setLevel(logging.WARNING)
        app.logger.addHandler(file_handler)

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'heroku': HerokuConfig,
    'default': HerokuConfig
}