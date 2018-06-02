from CDUTRestful.app.Exception.RequestError import RequestError


class TimeNotValidate(RequestError):
    def __init__(self, res_code=4100, res_msg='Token_validate'):
        super(RequestError, self).__init__()
        self.res_code = res_code
        self.res_msg = res_msg
