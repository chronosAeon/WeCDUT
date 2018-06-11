from flask import Flask
from CDUTRestful.app.models import db
from CDUTRestful.app.extensions import bcrypt


# def create_app():
#     app = Flask(__name__)  # type:Flask
#     app.config.from_object('app.secure')
#     app.config.from_object('app.setting')
#     register_blue_print(app)
#     db.init_app(app)
#     bcrypt.init_app(app)
#     with app.app_context():
#         db.create_all(app=app)
#     return app
#
#
# def register_blue_print(app):
#     from CDUTRestful.app.web import web_blueprint
#     app.register_blueprint(web_blueprint)
def create_app():
    app = Flask(__name__, static_folder='', static_url_path='')  # type:Flask
    # 读取配置文件
    app.config.from_object('app.secure')
    app.config.from_object('app.setting')
    # 注册蓝图
    register_blueprint(app)

    # 这个方法只是读取app.config的数据库配置文件
    db.init_app(app)
    # 方法一获取app
    # db.create_all(app=app)
    # 方法二通过上下文管理器推入核心appcontext
    with app.app_context():
        db.create_all(app=app)
    return app


def register_blueprint(app):
    # from CDUTRestful.app.web import web as web_print
    # from CDUTRestful.app.web.User import User
    from CDUTRestful.app.Login_web import web
    from CDUTRestful.app.WeCDUT import CDUT_Restful
    app.register_blueprint(web)
    app.register_blueprint(CDUT_Restful)