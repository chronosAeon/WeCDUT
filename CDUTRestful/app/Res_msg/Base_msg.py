import json


class Base_msg:
    def __init__(self, code=200, res_msg='success'):
        self.code = code
        self.res_msg = res_msg

    def res_json_back(self):
        return json.dumps({'code': self.code, 'res_msg': self.res_msg})
