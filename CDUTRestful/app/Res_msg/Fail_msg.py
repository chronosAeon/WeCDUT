from CDUTRestful.app.Res_msg.Base_msg import Base_msg


class Fail_msg(Base_msg):
    def __init__(self, code=400, res_msg='fail'):
        super(Fail_msg, self).__init__(code, res_msg)
