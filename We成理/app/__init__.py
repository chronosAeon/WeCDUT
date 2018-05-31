from flask import Flask
from app.models.__init__ import db

def create_app():
    app = Flask(__name__)
    app.config.from_object('app.secure')
    app.config.from_object('app.setting')
    register_blue_print(app)
    db.init_app(app)
    with app.app_context():
        db.create_all(app=app)
    return app

def register_blue_print(app):
    from app.web import web
    app.register_blueprint(web)