class RequestError(Exception):
    def __init__(self, res_code, res_msg):
        super(RequestError, self).__init__()
        self.res_code = res_code
        self.res_msg = res_msg

    def send_msg_back(self):
        res = {
            'res_code': self.res_code,
            'res_msg': self.res_msg
        }
        return res