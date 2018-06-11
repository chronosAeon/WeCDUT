from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from CDUTSpiders.ClassSpider.Data_Model.Class_spiderModel import get_UDM
from CDUTSpiders.ClassSpider.Data_Model.Semester_list_Model import Semester_list_model
from CDUTSpiders.ClassSpider.MixinModules.DbconfReadMixin import DbRMixin
from CDUTSpiders.ClassSpider.MixinModules.get_semester_listMixin import save_in_semester_listMixin
from CDUTSpiders.Class_BaseSpider.Class_BaseSpider import Class_BaseSpider
from CDUTSpiders.ClassSpider.Data_Model.TokenModel import Token_model
from CDUTSpiders.Token.CDUT_Token import Token
import requests
import time
from bs4 import BeautifulSoup
from CDUTSpiders.ClassSpider.helper.day_class import day_class
from CDUTSpiders.ClassSpider.helper.week_enum import week_enum
import json
import re


class ClassSpider(Class_BaseSpider, DbRMixin, save_in_semester_listMixin):
    '''
    所有的类都是为go方法服务的，构造方法为go获取服务
    '''
    @staticmethod
    def log_out(self,stu_number):
        '''
        登出
        :return:返回状态值
        '''
        user_item = self.Dbsession.query(self.UserData_model).filter_by(id=stu_number).first()
        if user_item:
            user_item.token = ''
            user_item.token_verify_time = ''
            self.Dbsession.commit()
            return True
        else:
            return False

    def Db_setting_init(self):
        '''
        复杂的数据初始化工作在这里
        :return:返回状态值
        '''
        engine_FormatString = 'mysql+mysqlconnector://{account}:{password}@{location}:{port}/{db_name}'
        enging_string = engine_FormatString.format(account=(self.read_Dbconfig('Db_account').replace('\'', '')),
                                                   password=(self.read_Dbconfig('Db_password').replace('\'', '')),
                                                   location=(self.read_Dbconfig('Db_Location').replace('\'', '')),
                                                   port=(self.read_Dbconfig('port').replace('\'', '')),
                                                   db_name=(self.read_Dbconfig('Db_name').replace('\'', '')))
        self.engine = create_engine(enging_string)
        Dbsession = sessionmaker(bind=self.engine)
        self.Dbsession = Dbsession()

    def Data_Model_init(self):
        '''
        数据库模型初始化
        '''
        # self.semester_list_model = Semester_list_model
        self.Token_model = Token_model
        UserDataModel = get_UDM(self.stu_number)
        self.UserData_model = UserDataModel

    def Data_table_init(self):
        '''
        初始化数据库表
        '''
        # self.semester_list_model.metadata.create_all(self.engine)
        self.Token_model.metadata.create_all(self.engine)
        self.UserData_model.metadata.create_all(self.engine)

    def Db_init(self):
        self.Db_setting_init()
        self.Data_Model_init()


    def Data_init(self):
        ClASSURL_format = "http://202.115.133.173:805/Classroom/ProductionSchedule/StuProductionSchedule.aspx?termid={}&stuID={}"
        self.class_format = ClASSURL_format

    def __init__(self, semester, stu_number, password, is_update=False):
        self.Data_init()
        self.semester = semester
        self.stu_number = stu_number
        self.password = password
        self.Db_key = str(self.semester) + '_' + str(self.stu_number)
        self.is_update = is_update
        self.Db_init()
        URL = 'http://202.115.133.173:805/Common/Handler/UserLogin.ashx'
        self.token = Token(URL, self.Token_model, self.stu_number, self.password, self.Dbsession)
        url = self.class_format.format(*[semester, stu_number])
        super().__init__(url)
        print(url)

    def _fetch_content(self, token):
        '''

        :param token:进入这里需要登录的token
        :param is_self: 是否是查找自己的数据
        :param stu_number: 如果是查找别人的信息要输入学生号
        :param stu_semester: 如果是查找别人的信息输入学期号
        :return:
        '''
        cookie_data = 'UserTokeID=' + token
        '''
        这里必须加头部信息，否则服务器内部报错
        '''
        header = {
            'Host': '202.115.133.173:805',
            'Connection': 'keep-alive',
            'Cache-Control': 'max-age=0',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.89 Safari/537.36',
            'Upgrade-Insecure-Requests': '1',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Referer': 'http://202.115.133.173:805/SelectCourse/',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.9',
        }
        header['Cookie'] = cookie_data

        res = requests.get(self.url, headers=header)
        res.encoding = 'utf-8'
        htmls = res.text
        return htmls

    def _fetch_other_content(self, token, stu_number, stu_semester):
        cookie_data = 'UserTokeID=' + token
        '''
        这里必须加头部信息，否则服务器内部报错
        '''
        header = {
            'Host': '202.115.133.173:805',
            'Connection': 'keep-alive',
            'Cache-Control': 'max-age=0',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.89 Safari/537.36',
            'Upgrade-Insecure-Requests': '1',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Referer': 'http://202.115.133.173:805/SelectCourse/',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.9',
        }
        header['Cookie'] = cookie_data

        # res = requests.get(self.url, headers=header)
        url = self.class_format.format(*[stu_semester, stu_number])
        print(url)
        res = requests.get(url, headers=header)
        res.encoding = 'utf-8'
        htmls = res.text
        return htmls

    def _analysis(self, html_str):
        # html = classSpider.file_handle.read()
        html = html_str
        soup = BeautifulSoup(html, 'lxml')
        soup.encode(encoding='utf-8')
        '''
        找到所有的table标签,按照不同的table标签做出不同的处理
        这里使用字典代替switch,key为索引
        '''
        table_router = {
            0: self.__first_tableHandle,
            1: self.__second_tableHandle,
            2: self.__third_tableHandle,
        }
        table_tags = soup.find_all('table')
        '''
        可以用如下方法把生成器变为list
        '''
        # table_list = list(table_tags)
        # print(len(table_list))
        tables_data = []
        for table_index, table_tag in enumerate(table_tags):
            tables_data.append(table_router.get(table_index)(table_tag))
        return tables_data

    def _handle_data(self, data):
        print(data[2])
        '''
        处理数据,第一个索引是是第几个table，第二个是第几周，第三个是第几天，存贮的是一个天课程对象
        '''
        handled_classdata = []
        class_array_str = ''
        for table_index, table in enumerate(data):

            if table_index == 1:
                print(table)
                for week in table[0]:
                    week_data = []
                    # print(week_data)
                    for day_data in week:
                        week_data.append(day_data.class_dic)
                    handled_classdata.append(week_data)
                class_array_str = json.dumps(table[1])
        handled_classDataStr = json.dumps(handled_classdata)
        class_detail = json.dumps(data[2])
        print(class_array_str)
        '''
        暂时先只返还课程数据
        '''
        return (handled_classDataStr, class_array_str, class_detail)

    def __first_tableHandle(self, table_tag):
        return 0

    def __third_tableHandle(self, table_tag):

        tds = table_tag.select('.detail')
        data_array = []
        # tds = trs[1].select('.detail')
        for item in tds:
            if item.text:
                '''
                这个地方可以处理detail数据
                '''
                data_array.append(item.text)
        return data_array

    def __get_data_arrayHandle(self, table_tag):
        '''
        这个地方必须是第二个tag
        :param table_tag:
        :return:
        '''
        pass

    def __second_tableHandle(self, table_tag):
        '''
        params table_tag传入bs4解析完的table_tag
        return 返回二维数组，每周为一个数组存贮每天的类信息
        '''
        '''
        这里开始对每一周的数据进行提取tr，然后就把数据给合适的格式放到mmongodb里面去
        '''
        '''
        tr_tags为每周数据
        '''
        tr_tags = table_tag.find_all('tr')
        all_data = []
        all_week_title = []
        for tr_index, tr_tag in enumerate(tr_tags):
            week_data = []
            day_dic = {1: None, 2: None, 3: None, 4: None, 5: None, 6: None,
                       7: None, 8: None, 9: None, 10: None, 11: None, 12: None}
            # week_list = [day_dic for item in range(12)]
            # week_list[0][1] = 2
            # for item in week_list:
            #     print(item[1])
            # day_date = None
            '''
            课表第二个tr之后才是课
            '''
            if tr_index > 1:
                '''
                td_tags为每节课数据
                '''
                # classSpider.write_file.write(str(tr_index-1)+'周的课\r')
                td_tags = tr_tag.find_all('td')
                '''
                每周有多少结课
                '''
                Aday_td = 12
                '''
                从星期几开始
                '''
                date_counter = 1
                class_counter = 0
                day_date = week_enum.Monday
                '''
                一周的数据遍历
                '''
                for tditem in td_tags:
                    # 标签如果是一个内含标签的话就没办法用string输出内部数据，就会输出Nonetype
                    # if tditem.stripped_strings is not None and tditem.stipped_string is None:
                    if 'align' in tditem.attrs:
                        content = ''
                        for item_string in tditem.stripped_strings:
                            content += item_string
                        span = int(tditem['colspan'])
                        for pace in range(1, span + 1):
                            day_dic[class_counter + pace] = content
                        class_counter += span

                    elif tditem['class'][0] == 'td1':
                        '''
                        去除开头第几周的表格内容
                        '''
                        pass
                    else:
                        '''
                        这里是应该是课名的位置没有课
                        '''
                        # content = 'NoClass\r'
                        content = 'NoClass'
                        day_dic[class_counter + 1] = content
                        class_counter += 1
                        # classSpider.write_file.write('NoClass'+'\r')
                    '''
                    课程计数器满足一天
                    '''
                    if class_counter >= Aday_td:
                        # classSpider.write_file.write(str(day_dic)+'\r')
                        '''
                        归位课程计数器
                        '''
                        class_counter = 0
                        '''
                        取出当天的日期
                        '''
                        if date_counter < 7:
                            day_date = week_enum(date_counter)
                            '''
                            把每天的数据和当天是星期几封装进类里面
                            '''
                            a_dayData = day_class(day_date, day_dic)
                            '''
                            这是个保留的测试部分，保留是为了提醒你千万别认为for in可以形成作用域
                            for in 里面的变量还有for in 里面遍历的都可以在外面获得
                            这里千万别用a_dayData这个名字，for in 在python3里面并不形成作用域
                            http://blog.cipherc.com/2015/04/25/python_namespace_and_scope/#for
                            '''
                            # for a_dayitem in week_data:
                            #     classSpider.write_file.write(
                            #         str(a_dayitem.class_dic)+'\r')
                            # classSpider.write_file.write(
                            #     '--------------------------------------\r')
                            # classSpider.write_file.write(str(a_dayData.class_dic)+'\r')

                            week_data.append(a_dayData)
                            date_counter += 1
                        elif date_counter == 7:
                            day_date = week_enum(date_counter)
                            '''
                            把每天的数据和当天是星期几封装进类里面
                            '''
                            a_dayData = day_class(day_date, day_dic)
                            week_data.append(a_dayData)
                            all_data.append(week_data)
                            date_counter = 1
                            week_data = []
                        else:
                            '''
                            星期计数器满足一周
                            这里面填写一周结束后的逻辑
                            这个地方可以不用归位，因为这一次做了就不用做了
                            '''
                            date_counter = 1
                            all_data.append(week_data)
        for tr_index, tr_tag in enumerate(tr_tags):
            if tr_index > 1:
                '''
                从第二个开始才是当前周数
                '''
                td_text = tr_tag.select_one('td').text
                # print(td_text)
                result = re.findall('周(.*)', td_text)
                all_week_title.append(result[0])
        # print(len(all_week_title))
        print(all_week_title)
        return (all_data, all_week_title)

    def _check_account(self, token):
        if not token:
            '''
            token错误
            '''
            return False
        else:
            '''
            获取token数据
            '''
            return token

    def go(self):
        URL = 'http://202.115.133.173:805/Common/Handler/UserLogin.ashx'
        token = Token(URL, self.Token_model, self.stu_number, self.password, self.Dbsession).fetch_token()
        check_result = self._check_account(token)
        if not check_result:
            '''
            账号错误
            '''
            return False
        else:
            '''
            账号正确创建用户表
            '''
            self.Data_table_init()
        refined_data = ''
        if self.is_update:
            '''
            更新数据的情况
            '''
            refined_data = self.get_refined_data_according_Token(token)
        else:
            '''
            先检查文件数据，不过这了可以考虑把这个给去掉了，基本用不到
            '''
            user_item = self.Dbsession.query(self.UserData_model).filter_by(id=self.Db_key).first()
            if user_item:
                '''
                如果数据库找到此数据
                '''
                response_dic = {
                    'class_timetable': user_item.json,
                    'class_classTime_array': user_item.class_array_title,
                    'class_array_detail': user_item.class_array_detail
                }

                refined_data = json.dumps(response_dic)
            else:
                '''
                如果没有找到就去爬
                '''
                refined_data = self.get_refined_data_according_Token(token)
        if 'Dbsession' in self.__dict__:
            '''
            这个地方是做了session的长久的私有化，这样会长时间占用连接，还有一种方式可以每次打开每次取
            但是哪种方式会频繁打开，这种方式要是对session有频繁操作，就可能会快一点
            '''
            self.Dbsession.close()
        print(refined_data)
        return refined_data

    def get_refined_data_according_Token(self, token):
        html_str = self._fetch_content(token)
        crude_data = self._analysis(html_str)
        refined_data = self._handle_data(crude_data)
        UserData = self.UserData_model(id=self.Db_key, time=time.time(), json=refined_data[0],
                                       class_array_title=refined_data[1], class_array_detail=refined_data[2])
        self.save_in_Database(self.Db_key, UserData)
        response_dic = {
            'class_timetable': refined_data[0],
            'class_classTime_array': refined_data[1],
            'class_array_detail': refined_data[2]
        }
        refined_data = json.dumps(response_dic)
        return refined_data

    def save_in_Database(self, id, UserData):
        user_item = self.Dbsession.query(self.UserData_model).filter_by(id=id).first()
        if user_item:
            '''
            如果存在id，更新
            '''
            user_item.json = UserData.json
            user_item.class_array_title = UserData.class_array_title
            user_item.class_array_detail = UserData.class_array_detail
            user_item.time = time.time()
            self.Dbsession.commit()
        else:
            self.Dbsession.add(UserData)
            # 提交即保存到数据库:
            self.Dbsession.commit()


if __name__ == '__main__':
    spider = ClassSpider(201702, 201505090228, '22028319961213352X', is_update=True)
    # spider.get_semester_list()
    spider.go()
