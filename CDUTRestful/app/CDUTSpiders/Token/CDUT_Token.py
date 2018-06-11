import hashlib

from CDUTSpiders.BaseSpider.BaseSpider import BaseSpider
import requests
import time
import re


class Token(BaseSpider):
    def __init__(self, url, TokenModel, stu_number, password, Db_session):
        self.Dbsession = Db_session
        self.TokenModel = TokenModel
        self.stu_number = stu_number
        self.password = password
        self.url = url
        super().__init__(url)

    def fetch_token(self, is_fresh=False):
        '''
        token持久化就优化了0.03秒
        :return:
        '''
        if not is_fresh:
            DB_TokenResult = self._get_token()
            Db_existToken = DB_TokenResult[0]
            # print(Db_existToken)
        else:
            Db_existToken = False
        if Db_existToken:
            return DB_TokenResult[1]
        else:
            password = self.cipherPassword(
                self.stu_number, time.time, self.password)
            # print(self.)
            # 'http://202.115.133.173:805/Common/Handler/UserLogin.ashx'
            Token_url = self.url
            '''
            这里的md5加密最好处理一下，不确定每一个md5算法是不是一样的，所以看是用python的md5
            还是python调用js的md5，但是对面的验证应该都没有问题
            '''
            data = {'Action': 'Login',
                    'userName': str(self.stu_number),
                    'sign': str(time.time)}
            data['pwd'] = password
            response = requests.post(Token_url, data)
            print('header:' + str(response.headers))
            print(response.headers)
            cookie = response.headers['Set-Cookie']
            print('cookie:' + str(cookie))
            '''
            这里采用正则表达式处理获取token值
            data存贮的sessionId和path两个数据
            '''
            data = re.findall('=(.*?);', cookie)
            print('data:' + str(data))
            '''
            ['0tjnrsihz5avnugw3hww5f3m', '/', '25c6c6a8-927d-42f0-801d-5cccacfd6c39']
            取第三位
            '''
            if len(data) <= 2:
                return False
            else:
                token_object = self.TokenModel(id=self.stu_number, token=data[2], time=time.time())
                self.save_in_Token_Db(self.stu_number, token_object)
                return data[2]

    @staticmethod
    def cipherPassword(user, timesign, pwd):

        '''
        加密算法
        '''
        # hex_md5(user + sign + hex_md5(pwd.trim()))
        h1 = hashlib.md5()
        pwd = str(pwd).strip()
        h1.update(pwd.encode(encoding='utf-8'))
        md_password = str(h1.hexdigest())
        h2 = hashlib.md5()
        code = str(user) + str(timesign) + md_password
        h2.update(code.encode(encoding='utf-8'))
        password = h2.hexdigest()
        return password

    def _get_token(self):
        '''
        这个方法从token表里面获取数据
        :return: 检查token是否可用，可用就可以返回不可用就直接返回
        '''
        token_item = self.Dbsession.query(self.TokenModel).filter_by(id=self.stu_number).first()
        if token_item is None:
            return False, ''
        else:
            # self.save_in_Database(id=self.id, )
            if time.time() - float(token_item.time) < 1800:
                '''
                如果token时间假设就是15分钟保持有效
                '''
                return True, token_item.token
            else:
                return False, ''

    def save_in_Token_Db(self, id, Tokenobject):
        token_item = self.Dbsession.query(self.TokenModel).filter_by(id=id).first()
        if token_item is not None:
            '''
            如果存在id，更新
            '''
            token_item.token = Tokenobject.token
            token_item.time = time.time()
            self.Dbsession.commit()
        else:
            self.Dbsession.add(Tokenobject)
            # 提交即保存到数据库:
            self.Dbsession.commit()
