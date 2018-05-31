from app.Exception.RequestError import RequestError


class LoginError(RequestError):
    def __init__(self, res_code, res_msg):
        super(LoginError, self).__init__(res_code, res_msg)
