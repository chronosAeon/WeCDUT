from CDUTRestful.app.Res_msg.Base_msg import Base_msg


class completeInfo(Base_msg):
    def __init__(self, code=406, res_msg='info_uncompleted'):
        super(completeInfo, self).__init__(code, res_msg)
