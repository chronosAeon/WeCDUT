from CDUTRestful.app.web import web
from CDUTRestful.app.Exception import LoginError
from CDUTRestful.app.Exception import RequestError


@web.errorhandler(LoginError)
def LoginError_handle(error):
    return error.send_msg_back()

