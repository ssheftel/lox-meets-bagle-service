from flask import Flask
from flask.ext.mongoengine import MongoEngine
from flask.ext.httpauth import HTTPBasicAuth
from flask.ext.mail import Mail

from config import config
db = MongoEngine()
auth = HTTPBasicAuth()

def create_app(config_name):
    app = Flask(__name__, static_url_path='')
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    db.init_app(app)
    from .api_1_0 import api as api_1_0_blueprint
    app.register_blueprint(api_1_0_blueprint, url_prefix='/api/v1.0')
    #Serve Static Files
    @app.route('/')
    def root(): return app.send_static_file('index.html')
    return app