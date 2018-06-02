from CDUTRestful.app.Exception import LoginError


class FakeTokenError(LoginError):
    def __init__(self, res_code='4000', res_msg='fake_token'):
        super(LoginError, self).__init__(res_code, res_msg)
