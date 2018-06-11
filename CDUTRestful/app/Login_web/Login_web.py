import json

import requests
from flask import request, jsonify

from CDUTRestful.app.Exception.LoginError import LoginError
from CDUTRestful.app.Res_msg.CompleteInfo_msg import completeInfo
from CDUTRestful.app.Res_msg.Complete_info_fail_msg import complete_info_fail_msg
from CDUTRestful.app.Res_msg.Fail_msg import Fail_msg
from CDUTRestful.app.Res_msg.Login_Wx import Login_wx_msg
from CDUTRestful.app.Res_msg.Success_msg import success_msg
from CDUTRestful.app.Res_msg.password_wrong import password_wrong
from CDUTRestful.app.models import User, db
from . import web


@web.route('/UserLogin', methods=['POST'])
def Wxlogin():
    '''
    接口完成，第一次的登陆注册，然后第一次注册完后检查用户信息是否完全。
    微信登陆注册用户，用户密码加密，返回持久化token，不过
    参数：code
    :return:token
    '''
    try:
        code = request.args.get('code')
    except LoginError as e:
        return jsonify(e.send_msg_back())
    except Exception:
        return jsonify(Fail_msg().res_json_back())
    else:
        WX_SERVER_URLFORMAT = r"https://api.weixin.qq.com/sns/iscode2session?appid={}&secret={}&is_code={}&grant_type=authorization_code"
        URL = WX_SERVER_URLFORMAT.format(*('wx48c3a1805c77abc9', '866c70d47b143581077e03076d9cce98', code))
        res = requests.get(URL)
        res_dict = json.loads(res.text)
        if 'openid' in res_dict and 'session_key' in res_dict:
            '''
            验证能从服务器能从到用户openid，但是没有办法判断是否是第一次登陆
            '''
            if User.query().filter_by(openid=res_dict['openid']):
                '''
                如果库里面有这个用户，检查用户的用户信息是否全整。
                '''
                result = check_user_info_complete(res_dict['openid'])
                if result:
                    '''
                    如果信息齐整
                    '''
                    return jsonify(success_msg().res_json_back())
                else:
                    '''
                    如果信息不齐整
                    '''
                    return jsonify(completeInfo().res_json_back())
            else:
                user_instance = User(res_dict['openid'], res_dict['session_key'])
                db.session.add(user_instance)
                db.session.commit()
                return jsonify(success_msg().res_json_back())
        else:
            '''
            不能从微信服务器拿到用户openid
            '''
            return jsonify(Fail_msg(res_msg='no openId').res_json_back())


def check_user_info_complete(openid):
    '''
    检查用户数据是否齐整
    :param openid: 用户id
    :return: true|false
    '''
    item = User.query().filter_by(openid=openid).first()
    if item.password and item.stu_id:
        '''
        检查id和password是否齐整
        '''
        return True
    else:
        '''
        id和password不齐整
        '''
        return False


@web.route('/index')
def hello_world():
    return 'Hello World!'


@web.route('/complete_info')
def Complete_info():
    if request.args['openid'] and request.args['session_key'] and request.args['stu_id'] and request.args['password']:
        openid = request.args['openid']
        session_key = request.args['session_key']
        stu_id = request.args['stu_id']
        password = request.args['password']
        user_instance = User(openid, session_key, stu_id=stu_id, password=password)
        db.session.add(user_instance)
        db.session.commite()
        return jsonify(complete_info_fail_msg().res_json_back())
    else:
        '''
        未提供正常的信息
        '''
        return jsonify(success_msg().res_json_back())


@web.route('/Login_in_web')
def Login_in_web():
    '''
    网页登陆
    :return:返回是否状态码
    '''
    account = request.args['account']
    password = request.args['password']
    item = User.query().filter_by(stu_id=account).fotst()
    if item:
        '''
        找得到stu_id的账号
        '''
        result = item.check_password(password)
        if result:
            return jsonify(password_wrong().res_json_back())
        else:
            return jsonify(success_msg().res_json_back())
    else:
        return jsonify(Login_wx_msg().res_json_back())

