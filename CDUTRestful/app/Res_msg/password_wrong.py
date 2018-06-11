from CDUTRestful.app.Res_msg.Base_msg import Base_msg


class password_wrong(Base_msg):
    def __init__(self, code=408, res_msg='info_uncompleted'):
        super(password_wrong, self).__init__(code,res_msg)
