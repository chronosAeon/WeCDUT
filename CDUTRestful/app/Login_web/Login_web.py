import json

import requests
from flask import request, jsonify

from CDUTRestful.app.Exception.LoginError import LoginError
from CDUTRestful.app.Login_web.Token_check.Token_check import Token
from CDUTRestful.app.Res_msg.CompleteInfo_msg import completeInfo
from CDUTRestful.app.Res_msg.Complete_info_fail_msg import complete_info_fail_msg
from CDUTRestful.app.Res_msg.Fail_msg import Fail_msg
from CDUTRestful.app.Res_msg.Login_Wx import Login_wx_msg
from CDUTRestful.app.Res_msg.Success_msg import success_msg
from CDUTRestful.app.Res_msg.Token_back import token_back
from CDUTRestful.app.Res_msg.password_wrong import password_wrong
from CDUTRestful.app.WeCDUT.CDUTSpider.CDUT_TOKEN import CDUTToken
from CDUTRestful.app.models import User, db
from . import web


@web.route('/UserCheckRavel', methods=['POST'])
def UserCheckRavel():
    '''
    1.直接登陆是没有传输值进入的，判断此openid数据库里面是否有账号密码，且账号密码可用（通过教务处去拿token），如果没有就放回新用户必须绑定。
    :return:
    '''
    try:
        code = request.form['code']
    except LoginError as e:
        return jsonify(e.send_msg_back())
    except Exception:
        return jsonify(Fail_msg().res_json_back())
    else:
        result_dict = get_openid_dict_by_code(code)
        if check_result_dict_validate(result_dict):
            # code有效
            if check_user_exist(result_dict['openid'])[0]:
                # 用户存在
                User_item = User.query.filter_by(open_id=result_dict['openid']).first()
                is_account_exist = check_account_password_exist(User_item)
                if is_account_exist:
                    # 该账号账号密码存在，验证这个教务处账号是否可用
                    password_show = User_item.decrypt('This is a key123', 'This is an IV456')
                    print(password_show)
                    token = CDUTToken(User_item.stu_id, password_show).fetch_token(is_fresh=True)

                    check_result = Token.check_account(token)
                    if check_result:
                        # 验证成功
                        return jsonify(token_back(User_item.token).res_json_back())
                    else:
                        # 验证失败
                        return jsonify(success_msg(code=406, res_msg='绑定的账号密码存在').res_json_back())
                else:
                    # 该账号账号密码不存在，需要重新绑定，可能是取消绑定，用户在，但是账号密码清空就不会在。
                    return jsonify(success_msg(code=406, res_msg='绑定的账号密码不存在').res_json_back())
            else:
                # 微信用户没有在表内,返回状态值，要用户绑定教务处
                return jsonify(completeInfo().res_json_back())
        else:
            # code无效
            return jsonify(Fail_msg(res_msg='no openId').res_json_back())


@web.route('/getUserInfoByToken', methods=['POST'])
def GetUserInfoByToken():
    if request.form.get('token'):
        token = request.form.get('token')
        print(token)
        user = User.query.filter_by(token=token).first()
        if user:
            account = user.stu_id
            password = user.decrypt('This is a key123', 'This is an IV456')
            return jsonify({'account': account, 'password': password, 'code': 200})
        else:
            return jsonify({'resInfo': 'your token is invalidated', 'code': 470})

    else:
        return jsonify({'resInfo': 'request or Params error', 'code': 470})


@web.route('/save_avatar_name', methods=['POST'])
def save_avatar_name():
    if request.form.get('token') and request.form.get('avatar_url') and request.form.get('name'):
        token = request.form.get('token')
        avatar_url = request.form.get('avatar_url')
        name = request.form.get('name')
        user_item = User.query.filter_by(token=token).first()
        if user_item:
            user_item.avatar_url = avatar_url
            user_item.nick_name = name
            db.session.commit()
            db.session.close()
            return jsonify(success_msg().res_json_back())
        else:
            return jsonify(Fail_msg(code=440, res_msg='token fail').res_json_back())
    else:
        return jsonify(Fail_msg(code=440, res_msg='数据表单信息不完整').res_json_back())


@web.route('/get_avatar_name', methods=['POST'])
def get_avatar_name():
    if request.form.get('token'):
        token = request.form.get('token')
        user_item = User.query.filter_by(token=token).first()
        if user_item:
            if user_item.avatar_url is not None and user_item.nick_name is not None:
                return jsonify({'code': 200, 'avatar_url': user_item.avatar_url, 'name': user_item.nick_name})
            else:
                return jsonify(Fail_msg(code=405, res_msg='no_UserInfo').res_json_back())
        else:
            return jsonify(Fail_msg(code=440, res_msg='token fail').res_json_back())
    else:
        return jsonify(Fail_msg(code=440, res_msg='数据表单信息不完整').res_json_back())


@web.route('/Login', methods=['POST'])
def Login():
    '''
    3种情况会调用这个接口，第一种是用户第一次登陆，第二种是取消绑定后账号密码被清空，第三种是账号密码验证被却确定是无效
    :return:
    '''
    try:
        code = request.form['code']
        account = request.form['account']
        password = request.form['password']
    except LoginError as e:
        return jsonify(e.send_msg_back())
    except Exception:
        return jsonify(Fail_msg().res_json_back())
    else:
        result_dict = get_openid_dict_by_code(code)
        if check_result_dict_validate(result_dict):
            # code有效
            if check_user_exist(result_dict['openid'])[0]:
                user_item = User.query.filter_by(openid=result_dict['openid']).first()
                # 用户存在
                token = CDUTToken(account, password).fetch_token(is_fresh=True)
                check_result = Token.check_account(token)
                if check_result:
                    # user_item = User.query.filter_by(open_id=result_dict['openid']).first()
                    user_item.stu_id = account
                    user_item.password = password
                    db.session.commit()
                    return jsonify(token_back(user_item.token).res_json_back())
                else:
                    # 教务处验证不正确
                    return jsonify(success_msg(code=440, res_msg='validate_fail').res_json_back())
            else:
                token = Token(account, password)
                token_string = token.fetch_token()
                check_result = Token.check_account(token_string)
                if check_result:
                    print('不存在逻辑')
                    # 用户不存在
                    new_instance = User(result_dict['openid'], result_dict['session_key'], stu_id=account,
                                        password=password)
                    db.session.add(new_instance)
                    db.session.commit()

                    return jsonify({'token': new_instance.token})
                    db.session.close()
                else:
                    # 教务处验证不正确
                    return jsonify(success_msg(code=440, res_msg='validate_fail').res_json_back())
        else:
            # code无效
            return jsonify(Fail_msg(res_msg='no openId').res_json_back())


@web.route('/quit', methods=['POST'])
def quit():
    if request.form.get('token'):
        token = request.form.get('token')
        user_item = User.query.filter_by(token=token).first()
        db.session.delete(user_item)
        db.session.commit()
        db.session.close()
        return jsonify(success_msg().res_json_back())
    else:
        return jsonify(Fail_msg(code=440, res_msg='token fail').res_json_back())


def get_openid_dict_by_code(code):
    WX_SERVER_URLFORMAT = "https://api.weixin.qq.com/sns/jscode2session?appid={}&secret={}&js_code={}&grant_type=authorization_code"
    URL = WX_SERVER_URLFORMAT.format(*('wx89ecbed4862b32f6', 'f333e972daec3b3185c92887547a1721', code))
    res = requests.get(URL)
    res_dict = json.loads(res.text)
    return res_dict


def check_result_dict_validate(res_dict):
    if 'openid' in res_dict and 'session_key' in res_dict:
        return True
    else:
        return False


def check_user_exist(openid):
    User_item = User.query.filter_by(open_id=openid).first()
    if User_item:
        return True, User_item
    else:
        return False, None


def check_account_password_exist(User_instance):
    '''
    检查账号密码存在
    :return:
    '''
    if User_instance.stu_id and User_instance.password:
        return True
    else:
        return False


def check_account_password_validate(stu_id, password):
    '''
    检查账号密码是有用的
    :return:
    '''
    URL = 'http://202.115.133.173:805/Common/Handler/UserLogin.ashx'
    token = Token(URL, stu_id, password).fetch_token()
    check_result = token.check_account(token)
    return check_result


# @web.route('/UserLogin', methods=['POST'])
# def Wxlogin():
#     '''
#     思路总结：就是token作为一次登陆操作凭证就可以一段时间不输入账号密码的凭证，而绑定是openid和account和password绑定的长时间的操作
#     接口完成，第一次的登陆注册，然后第一次注册完后检查用户信息是否完全。
#     微信登陆注册用户，用户密码加密，返回持久化token，不过
#     参数：code
#     :return:token
#     '''
#     try:
#         code = request.form['code']
#         print(code)
#     except LoginError as e:
#         return jsonify(e.send_msg_back())
#     except Exception:
#         return jsonify(Fail_msg().res_json_back())
#     else:
#         WX_SERVER_URLFORMAT = "https://api.weixin.qq.com/sns/jscode2session?appid={}&secret={}&js_code={}&grant_type=authorization_code"
#         URL = WX_SERVER_URLFORMAT.format(*('wxf9bcf40cebcc55a5', 'c69064347441e5e2c16e1f2e6d7217e6', code))
#         res = requests.get(URL)
#         res_dict = json.loads(res.text)
#         print(res_dict)
#         if 'openid' in res_dict and 'session_key' in res_dict:
#             '''
#             必须绑定账号密码
#             '''
#             if User.query.filter_by(open_id=res_dict['openid']).first():
#                 if 'token' in request.form:
#                     "检查token值,token验证，验证token是否可用"
#                     user_result = User.verify_auth_token(request.form['token'])
#                     if user_result[0]:
#                         '''
#                         如果信息齐整
#                         '''
#                         return jsonify(success_msg().res_json_back())
#                     else:
#                         '''
#                         如果信息不齐整
#                         '''
#                         return jsonify(user_result[1])
#                 elif 'account' in request.form and 'password' in request.form:
#                     'token失效账号密码登陆'
#                     if User.query.filter_by(stu_id=request.form['account']):
#                         '''
#                         找到账号
#                         '''
#                         user_item = User.query.filter_by(stu_id=request.form['account']).first()
#                         print('old_token:' + user_item.token)
#                         check_result = user_item.check_password(request.form['password'])
#                         if check_result:
#                             '''账号密码正确，重新生成新的token更新数据库，返回给客户端'''
#                             new_token = user_item.refresh_auth_token(request.form['account'],
#                                                                      request.form['password'])
#                             print(new_token)
#                             return jsonify({'code': 200, 'new_token': new_token})
#                         else:
#                             '''密码错误，返回客户端错误信息'''
#                             return jsonify(Fail_msg(code=405, res_msg='password wrong').res_json_back())
#                     else:
#                         '''
#                         没有账号，返回客户端没有账号
#                         '''
#                         return jsonify(Fail_msg(code=420, res_msg='no the account'))
#             else:
#                 user_instance = User(res_dict['openid'], res_dict['session_key'], stu_id=request.form['account'],
#                                      password=request.form['password'])
#                 db.session.add(user_instance)
#                 db.session.commit()
#                 return jsonify(success_msg().res_json_back())
#         else:
#             '''
#             不能从微信服务器拿到用户openid
#             '''
#             return jsonify(Fail_msg(res_msg='no openId').res_json_back())


def check_user_info_complete(openid):
    '''
    检查用户数据是否齐整
    :param openid: 用户id
    :return: true|false
    '''
    item = User.query.filter_by(openid=openid).first()
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

# @web.route('/complete_info')
# def Complete_info():
#     if request.args['openid'] and request.args['session_key'] and request.args['stu_id'] and request.args[
#         'password']:
#         openid = request.args['openid']
#         session_key = request.args['session_key']
#         stu_id = request.args['stu_id']
#         password = request.args['password']
#         user_instance = User(openid, session_key, stu_id=stu_id, password=password)
#         db.session.add(user_instance)
#         db.session.commite()
#         return jsonify(complete_info_fail_msg().res_json_back())
#     else:
#         '''
#         未提供正常的信息
#         '''
#         return jsonify(success_msg().res_json_back())


# @web.route('/Login_in_web')
# def Login_in_web():
#     '''
#     网页登陆
#     :return:返回是否状态码
#     '''
#     account = request.args['account']
#     password = request.args['password']
#     item = User.query().filter_by(stu_id=account).fotst()
#     if item:
#         '''
#         找得到stu_id的账号
#         '''
#         result = item.check_password(password)
#         if result:
#             return jsonify(password_wrong().res_json_back())
#         else:
#             return jsonify(success_msg().res_json_back())
#     else:
#         return jsonify(Login_wx_msg().res_json_back())
