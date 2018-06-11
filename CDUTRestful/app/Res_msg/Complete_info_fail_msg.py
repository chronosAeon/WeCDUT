from CDUTRestful.app.Res_msg.Base_msg import Base_msg


class complete_info_fail_msg(Base_msg):
    def __init__(self, code=408, res_msg='info_get_error'):
        '''
        :param code:408 信息填入错误
        :param res_msg: 报错信息
        '''
        super(complete_info_fail_msg, self).__init__(code, res_msg)
