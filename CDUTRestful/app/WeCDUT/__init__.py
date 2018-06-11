from flask import Blueprint

CDUT_Restful = Blueprint('CDUT_Restful', __name__)
from CDUTRestful.app.WeCDUT import WeCDUT