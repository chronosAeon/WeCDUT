import json
import time
from bs4 import BeautifulSoup
from CDUTSpiders.Token.CDUT_Token import Token
import lxml


def semester_list_decorator(func):
    def across_Db(*args):
        print(args[0].stu_number)
        grade = str(args[0].stu_number)[0:4]
        semester_list_item = args[0].Dbsession.query(args[0].semester_list_model).filter_by(
            grade=grade).first()
        # print(semester_list_item.list)
        if semester_list_item is None:
            # print('ok')
            list = func(args[0])
            list_serized = json.dumps(list)
            semester_list_object = args[0].semester_list_model(grade=grade, time=time.time(), list=list_serized)

            args[0].save_in_semester_list(grade, semester_list_object)
            return list
            '''
            存进数据库
            '''
        else:
            '''
            返回数据库里面的条目
            '''
            return json.loads(semester_list_item.list)

    return across_Db


class save_in_semester_listMixin:
    def __init__(self):
        # print('ok')
        pass

    def save_in_semester_list(self, grade, semester_list_object):
        semester_list_item_inDb = self.Dbsession.query(self.semester_list_model).filter_by(
            grade=grade).first()
        print(semester_list_object.list)
        if semester_list_item_inDb is not None:
            semester_list_item_inDb.list = semester_list_object.list
            semester_list_item_inDb.time = time.time()
            self.Dbsession.commit()
        else:
            print('no')
            self.Dbsession.add(semester_list_object)
            # 提交即保存到数据库:
            self.Dbsession.commit()

    # @semester_list_decorator
    @staticmethod
    def get_semester_list(stu_num):
        URL = 'http://202.115.133.173:805/Common/Handler/UserLogin.ashx'
        # self.token = Token(URL, self.Token_model, self.stu_number, self.password, self.Dbsession)
        year = int(time.strftime("%Y", time.localtime()))
        start_year = int(str(stu_num)[0: 4])
        yearfull_list_int = []
        checked_list_int = []
        checking_list_string = []
        term_list = ['01', '02']
        while True:
            # 对于2018年就是2016年是非常确定是有的
            if start_year < year - 1:
                yearfull_list_int.extend(map(lambda x: int(str(start_year) + x), term_list))
                start_year += 1
            elif start_year == year - 1 or start_year == year:
                # 审查当前年份的学期是否有课程表
                checking_list_string.extend(list(map(lambda x: str(start_year) + x, term_list)))
                start_year += 1
            else:
                break
        print(yearfull_list_int)
        checked_list_int.extend(yearfull_list_int)
        # for item in checking_list_string:
        #     if self.check_curriculum_exist(item):
        #         checked_list_int.append(int(item))
        # print(checked_list_int)
        return checked_list_int, checking_list_string

    def clear_semester_list(self):
        Semester_list_items = self.Dbsession.query(self.semester_list_model).filter_by().all()
        for Semester_list_item in Semester_list_items:
            self.Dbsession.delete(Semester_list_item)
        self.Dbsession.commit()

    def check_curriculum_exist(self, semester):
        token = self.token.fetch_token()
        htmls = self._fetch_other_content(token, self.stu_number, semester)
        soup = BeautifulSoup(htmls, 'lxml')
        soup.encode(encoding='utf-8')
        table_tags = soup.find_all('table')
        for table in table_tags:
            if table['class'][0] == 'tab2':
                if table.find_all('b'):
                    return True
                else:
                    return False

    # def save_in_semester_list(self, grade, semester_list_object):
    #     semester_list_item = self.Dbsession.query(self.semester_list_model).filter_by(
    #         grade=grade).first()
    #     if semester_list_item is not None:
    #         semester_list_item.list = semester_list_object.list
    #         semester_list_item.time = time.time()
    #         self.Dbsession.commit()
    #     else:
    #         self.Dbsession.add(semester_list_object)
    #         # 提交即保存到数据库:
    #         self.Dbsession.commit()
