from flask import Blueprint

web = Blueprint('web', __name__)
from CDUTRestful.app.web import User
from CDUTRestful.app.Exception import *