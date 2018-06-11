from CDUTRestful.app.Res_msg.Base_msg import Base_msg


class Login_wx_msg(Base_msg):
    def __init__(self, code=412, res_msg='please Login in wx first'):
        super(Login_wx_msg, self).__init__(code, res_msg)
