from CDUTRestful.app.Exception.RequestError import RequestError


class LoginError(RequestError):
    def __init__(self, res_code='450', res_msg='login_fail'):
        super(LoginError, self).__init__(res_code, res_msg)
