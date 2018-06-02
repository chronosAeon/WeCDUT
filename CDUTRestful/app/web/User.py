import json

import requests
from flask import request, jsonify

from CDUTRestful.app.Exception.LoginError import LoginError
from CDUTRestful.app.models import User, db
from . import web


@web.route('/UserLogin', methods=['POST'])
def Wxlogin():
    '''
    微信登陆，传入code
    参数：code
    :return:token
    '''
    try:
        code = request.args.get('code')
    except LoginError as e:
        return jsonify({'msg': e.send_msg_back()})
    except Exception:
        return jsonify({'res_code': '400', 'res_msg': 'fail'})
    else:
        WX_SERVER_URLFORMAT = r"https://api.weixin.qq.com/sns/iscode2session?appid={}&secret={}&is_code={}&grant_type=authorization_code"
        URL = WX_SERVER_URLFORMAT.format(*('wx48c3a1805c77abc9', '866c70d47b143581077e03076d9cce98', code))
        res = requests.get(URL)
        res_dict = json.loads(res.text)
        if 'openid' in res_dict and 'session_key' in res_dict:
            '''
            验证能从微信拿到用户openid
            '''
            user_instance = User(res_dict['openid'], res_dict['session_key'])
            db.session.add(user_instance)
            db.session.commit()
            return jsonify({'res_code': '200', 'res_msg': 'success'})
        else:
            '''
            不能从微信服务器拿到用户openid
            '''
            return jsonify({'res_code': '400', 'res_msg': 'open_id_error'})
