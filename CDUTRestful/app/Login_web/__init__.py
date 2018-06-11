from flask import Blueprint

web = Blueprint('Login_web', __name__)
from CDUTRestful.app.Login_web import Login_web
