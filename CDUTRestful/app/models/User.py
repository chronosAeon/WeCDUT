from typing import Text

from CDUTRestful.app.Exception import FakeTokenError, TimeNotValidate
from CDUTRestful.app.extensions import bcrypt
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from CDUTRestful.app.models import db
from datetime import datetime
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from itsdangerous import SignatureExpired, BadSignature
from flask import current_app

from CDUTRestful.app.web import User


class User(db.Model):
    '''
    对这个操作可以这么理解，flask-sqlAlchemy首先在创建表阶段会以类属性创建表，
    会以对象数据加入行
    '''
    id = Column(Integer, primary_key=True)
    open_id = Column(Text, nullable=False, unique=True)
    session_id = Column(Text, nullable=False, unique=True)
    token = Column(String(255), unique=True)
    stu_id = Column(String(255), nullable=False, unique=True)
    token_verify_time = Column(DateTime)
    password = Column(String(255), nullable=False)
    account_validate = Column(Boolean, nullable=False)
    token_forever = Column(Boolean, nullable=False)

    def __init__(self, open_id, session_id, stu_id='', password='', token_verify_time=datetime.now(),
                 account_validate=True,
                 token_forever=False):
        '''
        账号初始化
        :param open_id:加密openid
        :param session_id:加密sessionid
        :param token:是id账号密码的加密，然后只有对应的key才有可能还原
        :param stu_id:学生账号
        :param token_verify_time:token的有效期
        :param password:加密后的密码
        :param account_validate:账号的的有效期
        :param token_forever:token是否是永远有效，如果是就不会每几天就要看一次课表
        '''
        self.open_id = bcrypt.generate_password_hash(open_id)
        self.session_id = bcrypt.generate_password_hash(session_id)
        self.token_verify_time = token_verify_time
        self.token = self.generate_auth_token(stu_id, password, token_verify_time)
        if password and stu_id:
            self.stu_id = stu_id
            self.password = bcrypt.generate_password_hash(password)
        else:
            self.stu_id = ''
            self.password = ''
        self.account_validate = account_validate
        self.token_forever = token_forever

    def generate_auth_token(self, stu_id, password, token_verify_time):
        s = Serializer(current_app.config['SECRET_KEY'], expires_in=current_app.config['Token_duration'])
        return s.dumps({'stu_id': stu_id, 'password': password, 'time_validate': token_verify_time})

    @staticmethod
    def verify_auth_token(token):
        '''
        :param token: token
        :return:返回User
        '''
        '''
        通过解析完的data抛出异常并且处理，如果当前账户是token合格的就，直接拆解token获取明文信息
        如果当前token是不合格的那么就对应账号密码，如果都对就那当前的明文访问学校。
        '''
        try:
            data = Serializer.loads(token)
        except SignatureExpired:
            '''
            时间戳过期,这里要考虑一下有些用户不想输入账号密码，就永远托管在服务器。
            '''
            return TimeNotValidate.TimeNotValidate.send_msg_back()
        except BadSignature:
            '''
            信息损坏
            '''
            return FakeTokenError.FakeTokenError.send_msg_back()
        user = User.query.filter_by(stu_id=data['stu_id'])
        return user

    def check_password(self, password):
        '''
        检查密码是否正确
        :param password: 明文密码
        :return: true|false
        '''
        return bcrypt.check_password_hash(self.password, password)

    def check_stu_id(self, account):
        '''
        检查密码是否正确
        :param account: 明文账号
        :return: true|false
        '''
        return self.stu_id == account
