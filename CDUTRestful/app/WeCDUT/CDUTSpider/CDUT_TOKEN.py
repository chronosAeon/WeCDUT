from datetime import datetime
import hashlib
import re
import time

import requests
from CDUTRestful.app.models.User_token import User_token
from CDUTRestful.app.models import db


class CDUTToken:
    def __init__(self, stu_number, password, db_session=db.session, token_model=User_token, token_url=None):
        '''
        CDUT_Token初始化
        :param TokenModel:Token类名
        :param stu_number: 教务处学号
        :param password: 教务处密码
        :param Db_session: 数据库持久化操作
        :param token_url: 初始化为教务处分发token的url
        '''
        if token_url:
            self.token_url = token_url
        else:
            self.token_url = 'http://202.115.133.173:805/Common/Handler/UserLogin.ashx'
        self.db_session = db_session
        self.token_model = token_model
        self.stu_number = stu_number
        self.password = password

    def fetch_token(self, is_fresh=False):
        '''
        token持久化就优化了0.03秒，持久化不在于加速了多少，在于多次访问就不能再得到
        :return:
        '''
        if is_fresh:
            Db_existToken = False
        else:
            DB_TokenResult = self._get_token()
            Db_existToken = DB_TokenResult[0]
        if Db_existToken:
            return DB_TokenResult[1]
        else:
            time_sign = time.time()
            password = self.cipher_password(
                self.stu_number, self.password, time_sign)
            '''
            这里的md5加密最好处理一下，不确定每一个md5算法是不是一样的，所以看是用python的md5
            还是python调用js的md5，但是对面的验证应该都没有问题
            '''
            data = {'Action': 'Login',
                    'userName': str(self.stu_number),
                    'sign': str(time_sign)}
            data['pwd'] = password
            response = requests.post(self.token_url, data)
            # print('header:' + str(response.headers))
            # print(response.headers)
            cookie = response.headers['Set-Cookie']
            # print('cookie:' + str(cookie))
            '''
            这里采用正则表达式处理获取token值
            data存贮的sessionId和path两个数据
            '''
            data = re.findall('=(.*?);', cookie)
            # print('data:' + str(data))
            '''
            ['0tjnrsihz5avnugw3hww5f3m', '/', '25c6c6a8-927d-42f0-801d-5cccacfd6c39']
            取第三位
            '''
            if len(data) <= 2:
                return False
            else:
                token_object = self.token_model(self.stu_number, data[2], datetime.now())
                self.save_in_token_db(self.stu_number, token_object)
                return data[2]

    @staticmethod
    def cipher_password(user, pwd, time_sign):
        '''
        教务处模拟登陆加密算法
        :param time_sign: 时间戳
        :param user: 用户学号
        :param pwd: 用户密码
        :return: 返回登陆教务处的密码戳
        '''
        h1 = hashlib.md5()
        pwd = str(pwd).strip()
        h1.update(pwd.encode(encoding='utf-8'))
        md_password = str(h1.hexdigest())
        h2 = hashlib.md5()
        code = str(user) + str(time_sign) + md_password
        h2.update(code.encode(encoding='utf-8'))
        password = h2.hexdigest()
        return password

    def _get_token(self):
        '''
        这个方法从token表里面获取数据
        :return: 检查token是否可用，可用就可以返回不可用就直接返回
        '''
        token_item = self.token_model.query.filter_by(stu_id=self.stu_number).first()
        if token_item:
            if (datetime.now() - token_item.generate_time).seconds < 1800:
                '''
                如果token时间假设就是15分钟保持有效
                '''
                return True, token_item.class_token
            else:
                return False, ''
        else:
            return False, ''

    def save_in_token_db(self, stu_id, token_object):
        token_item = self.db_session.query(self.token_model).filter_by(stu_id=stu_id).first()
        if token_item:
            token_item.class_token = token_object.class_token
            token_item.generate_time = token_object.generate_time
            self.db_session.commit()
        else:
            self.db_session.add(token_object)
            # 提交即保存到数据库:
            self.db_session.commit()
