import json

from CDUTRestful.app.Res_msg.Base_msg import Base_msg


class token_back(Base_msg):
    def __init__(self, token):
        self.token = token
        super(token_back, self).__init__()

    def res_json_back(self):
        return json.dumps({'code': self.code, 'res_msg': self.res_msg, 'token': self.token})
