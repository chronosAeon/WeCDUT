import json


class RequestError(Exception):
    '''
    访问基础异常类
    '''

    def __init__(self, res_code=400, res_msg='request_fail'):
        super(RequestError, self).__init__()
        self.res_code = res_code
        self.res_msg = res_msg

    def send_msg_back(self):
        res = {
            'res_code': self.res_code,
            'res_msg': self.res_msg
        }
        return json.dumps(res)
