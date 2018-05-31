from flask import request, jsonify

from app.Exception.LoginError import LoginError
from . import web


@web.route('/UserLogin')
def login():
    '''
    微信登陆，传入code
    参数：code
    :return:
    '''
    try:
        code = request.args.get('code')
    except LoginError as e:
        return jsonify(e.send_msg_back())
    except Exception:
        return jsonify({'res_code': '400', 'res_msg': 'fail'})
    else:
