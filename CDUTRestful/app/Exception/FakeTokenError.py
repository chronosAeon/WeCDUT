from CDUTRestful.app.Exception.RequestError import RequestError


class FakeTokenError(RequestError):
    def __init__(self, res_code='4000', res_msg='fake_token'):
        super(RequestError, self).__init__(res_code, res_msg)
