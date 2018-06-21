import time

from flask import request, jsonify

from CDUTRestful.app import db
from CDUTRestful.app.Res_msg.Fail_msg import Fail_msg
from CDUTRestful.app.Res_msg.Success_msg import success_msg
from CDUTRestful.app.WeCDUT.CDUTSpider.BookBriefSpider import BookSearchSpider
from CDUTRestful.app.WeCDUT.CDUTSpider.BookDetailSpider import BookDetailSpider
from CDUTRestful.app.WeCDUT.CDUTSpider.ClassSpider import ClassSpider
from CDUTRestful.app.WeCDUT.CDUTSpider.EmptyClassRoom import EmptyClassRoom
from CDUTRestful.app.WeCDUT.CDUTSpider.GradeSpider import GradesSpider
from CDUTRestful.app.models import User
from CDUTRestful.app.models.Mapinfo import MapInfo
from . import CDUT_Restful


@CDUT_Restful.route('/curriculum', methods=['POST'])
def curriculum():
    if request.form.get('stu_number') and request.form.get('password') and request.form.get('semester'):
        # 前端已经校验了位数和密码
        stu_number = request.form.get('stu_number')
        password = request.form.get('password')
        semester = request.form.get('semester')
        if request.form.get('isfresh'):
            # 强制刷新数据
            class_data = ClassSpider(semester, stu_number, password, is_update=True).get_class_info()
        else:
            class_data = ClassSpider(semester, stu_number, password).get_class_info()
        return jsonify(class_data)
    else:
        # 数据残缺
        return jsonify(Fail_msg(code=440, res_msg='数据表单信息不完整').res_json_back())


@CDUT_Restful.route('/GPA', methods=['POST'])
def gpa():
    if request.form.get('account') and request.form.get('password'):
        account = request.form.get('account')
        password = request.form.get('password')
        spider = GradesSpider(account, password)
        gpa, data = spider.go()
        resultData = {
            'GPA': gpa,
            'data': data
        }
        return jsonify(resultData)
        # 检测表单完整
    else:
        return jsonify(Fail_msg(code=440, res_msg='数据表单信息不完整').res_json_back())


@CDUT_Restful.route('/BookList', methods=['POST'])
def book_list():
    if request.form.get('book_name'):
        book_name = request.form.get('book_name')
        spider = BookSearchSpider(book_name)
        data = spider.Fetch_content()
        array_object = spider.get_item_lists(data)
        if array_object:
            text = spider.get_jsonify_list_data(array_object)
            return text, 200, {'content-type': 'application/json'}
        else:
            return 'noParam', 200, {'content-type': 'html/text'}
    else:
        return jsonify(Fail_msg(code=440, res_msg='数据表单信息不完整').res_json_back())


@CDUT_Restful.route('/BookDetail', methods=['POST'])
def BookDetail():
    '''
    这里ip代理池，后台访问豆瓣api突破单ip每分钟访问限制
    :return:
    '''
    if request.form.get('bookdetail_url'):
        book_detail_url = request.form.get('bookdetail_url')
        spider = BookDetailSpider(book_detail_url)
        data = spider.get_book_item_content()
        detail_object = spider.get_book_item_object(data)
        text = spider.get_jsonify_item_data(detail_object)
        return text, 200, {'content-type': 'application/json'}
    else:
        return jsonify(Fail_msg(code=440, res_msg='数据表单信息不完整').res_json_back())


@CDUT_Restful.route('/getEmptyClassInfo', methods=['POST'])
def getEmptyClassInfo():
    if request.form.get('date') and request.form.get('building') and request.form.get('account') and request.form.get(
            'password'):
        account = request.form.get('account')
        password = request.form.get('password')
        date = request.form.get('date')
        building = request.form.get('building')
        spider = EmptyClassRoom(account,
                                password, date, building)
        try:
            result = spider.go()
            return result, 200, {'content-type': 'application/json'}
        except Exception:
            return 'param fail', 202
    else:
        return jsonify(Fail_msg(code=440, res_msg='数据表单信息不完整').res_json_back())


@CDUT_Restful.route('/addMapInfo', methods=['POST'])
def addMapInfo():
    '''
    id = Column(Integer, primary_key=True)
    marker_latitude = Column(Float)
    marker_longitude = Column(Float)
    submit_user = Column(String(255))
    description = Column(Text)
    validate_time = Column(DateTime)
    :return:
    '''
    if request.form.get('marker_latitude') and request.form.get('marker_longitude') and request.form.get(
            'submit_user') and request.form.get('description'):
        marker_latitude = request.form.get('marker_latitude')
        marker_longitude = request.form.get('marker_longitude')
        submit_user = request.form.get('submit_user')
        description = request.form.get('description')
        if MapInfo.query.filter_by(submit_user=submit_user).first():
            '''
            如果找到用户,更新
            '''
            map_info = MapInfo.query.filter_by(submit_user=submit_user).first()
            map_info.marker_latitude = marker_latitude
            map_info.marker_longitude = marker_longitude
            db.session.commit()
            db.session.close()
        else:
            '''
            如果找不到用户，就添加
            '''
            new_mapInfo = MapInfo(marker_latitude, marker_longitude, submit_user, description)
            db.session.add(new_mapInfo)
            db.session.commit()
            db.session.close()
        return jsonify(success_msg().res_json_back())
    else:
        return jsonify(Fail_msg(code=440, res_msg='数据表单信息不完整').res_json_back())


@CDUT_Restful.route('/deleteMapInfo', methods=['POST'])
def deleteMapInfo():
    pass


@CDUT_Restful.route('/getMapInfo', methods=['POST'])
def getMapInfo():
    infos = MapInfo.query.filter_by().all()
    res_array = []
    for info in infos:
        res_array.append(info.return_back())
    return jsonify({'result': res_array, 'code': 200})
