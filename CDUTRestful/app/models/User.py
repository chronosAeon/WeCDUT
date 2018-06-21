import uuid

from Crypto.Cipher import AES

from Crypto.SelfTest.st_common import b2a_hex, a2b_hex
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from CDUTRestful.app.models import db
from datetime import datetime




class User(db.Model):
    '''
    对这个操作可以这么理解，flask-sqlAlchemy首先在创建表阶段会以类属性创建表，
    会以对象数据加入行
    '''
    id = Column(Integer, primary_key=True)
    open_id = Column(String(255), nullable=False, unique=True)
    session_id = Column(String(255), nullable=False, unique=True)
    token = Column(String(255), default=None)
    stu_id = Column(String(255), nullable=False, unique=True)
    token_verify_time = Column(DateTime)
    password = Column(String(255), nullable=False)
    account_validate = Column(Boolean, nullable=False)
    token_forever = Column(Boolean, nullable=False)
    avatar_url = Column(String(255))
    nick_name = Column(String(255))

    def __init__(self, open_id, session_id, stu_id='', password='', token_verify_time=datetime.now(),
                 account_validate=True,
                 token_forever=False):
        '''
        账号初始化
        :param open_id:openid
        :param session_id:sessionid
        :param token:是id账号密码的加密，然后只有对应的key才有可能还原
        :param stu_id:学生账号
        :param token_verify_time:token的有效期
        :param password:加密后的密码
        :param account_validate:账号的的有效期
        :param token_forever:token是否是永远有效，如果是就不会每几天就要看一次课表
        '''
        
        self.mode = AES.MODE_CBC
        self.open_id = open_id
        self.session_id = session_id
        self.token_verify_time = token_verify_time
        if stu_id and password and token_verify_time:
            self.token = uuid.uuid4().hex
        else:
            self.token = None
        if password and stu_id:
            self.stu_id = stu_id
            self.password = self.encrypt(password)
        else:
            self.stu_id = ''
            self.password = ''
        self.account_validate = account_validate
        self.token_forever = token_forever

    def encrypt(self, password):
        cryptor = AES.new(self.key_one, self.mode, self.key_two)
        # 这里密钥key 长度必须为16（AES-128）、24（AES-192）、或32（AES-256）Bytes 长度.目前AES-128足够用
        length = 16
        count = len(password)
        add = length - (count % length)
        text = password + ('\0' * add)
        ciphertext = cryptor.encrypt(text)
        # 因为AES加密时候得到的字符串不一定是ascii字符集的，输出到终端或者保存时候可能存在问题
        # 所以这里统一把加密后的字符串转化为16进制字符串
        return b2a_hex(ciphertext)

    def decrypt(self, key_one, key_two, mode=AES.MODE_CBC):
        cryptor = AES.new(key_one, mode, key_two)
        plain_text = cryptor.decrypt(a2b_hex(self.password))
        print(plain_text.decode())
        text = plain_text.decode()
        return text.rstrip('\0')

    def check_stu_id(self, account):
        '''
        检查密码是否正确
        :param account: 明文账号
        :return: true|false
        '''
        return self.stu_id == account
