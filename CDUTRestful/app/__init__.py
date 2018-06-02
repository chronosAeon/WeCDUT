from flask import Flask
from CDUTRestful.app.models import db
from CDUTRestful.app.extensions import bcrypt


def create_app():
    app = Flask(__name__)
    app.config.from_object('app.secure')
    app.config.from_object('app.setting')
    register_blue_print(app)
    db.init_app(app)
    bcrypt.init_app(app)
    with app.app_context():
        db.create_all(app=app)
    return app


def register_blue_print(app):
    from CDUTRestful.app.web import web
    app.register_blueprint(web)
