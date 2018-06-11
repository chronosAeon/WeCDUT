from CDUTRestful.app.Res_msg.Base_msg import Base_msg


class success_msg(Base_msg):
    def __init__(self, code=200, res_msg='success'):
        super(success_msg, self).__init__(code, res_msg)
