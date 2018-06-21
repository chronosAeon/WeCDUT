from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()
from CDUTRestful.app.models.User import User
from CDUTRestful.app.models.ClassInfo import ClassInfo
from CDUTRestful.app.models.User_token import User_token