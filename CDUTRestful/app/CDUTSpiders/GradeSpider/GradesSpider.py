# -*- coding:utf-8 -*-
import requests
import json
from bs4 import BeautifulSoup
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from CDUTSpiders.BaseSpider.BaseSpider import BaseSpider
from CDUTSpiders.ClassSpider.Data_Model.TokenModel import Token_model
from CDUTSpiders.ClassSpider.MixinModules.DbconfReadMixin import DbRMixin
from CDUTSpiders.GradeSpider.stu_grade import Stu_grade
from CDUTSpiders.Token.CDUT_Token import Token

Grades_url = 'http://202.115.133.173:805/SearchInfo/Score/ScoreList.aspx'
Token_url = 'http://202.115.133.173:805/Common/Handler/UserLogin.ashx'


# class MaxScore_list(list):
#     def append(self, object: _T):
#         pass

class GradesSpider(Token, DbRMixin):

    def __init__(self, stu_number, password):
        self.Db_setting_init()
        # super(BaseSpider,self).__init__(url=Grades_url)
        super().__init__(Token_url, Token_model, stu_number, password, self.Dbsession)
        self.stu_number = stu_number
        self.password = password

    def Db_setting_init(self):
        '''
        复杂的数据初始化工作在这里
        :return:
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

    def fetch_gradesContent(self):
        '''
        获取成绩html内容
        :return:html内容
        '''
        token = self.fetch_token()
        print(token)
        token_string = 'UserTokeID={0}'.format(token)
        header = {
            'Host': '202.115.133.173:805',
            'Connection': 'keep-alive',
            'Cache-Control': 'max-age=0',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.89 Safari/537.36',
            'Upgrade-Insecure-Requests': '1',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Referer': 'http://202.115.133.173:805/SelectCourse/',
            'Cookie': '',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.9'
        }
        header['Cookie'] = token_string
        '''
        这个地方的headers是可选参数不是位置参数所以就必须显示的申明headers = header
        '''
        res = requests.get(Grades_url, headers=header)
        res.encoding = 'utf-8'
        html_text = res.text
        return html_text

    def analysis_grades(self, data):
        '''
        分析处理html
        :return: list数组数组里面存贮的是stu_grade对象
        '''

        soup = BeautifulSoup(data, 'lxml')
        soup.encode(encoding='utf-8')
        ul_tags = soup.find_all('ul')
        li_tags = ul_tags[5].find_all('li')
        allclass_grade = list()
        for li_tag in li_tags:
            params_list = list()
            if li_tag['class'][0] != 'head':
                divs_tags = li_tag.find_all('div')
                for div_tag in divs_tags:
                    params_list.append(div_tag.string.strip())
                allclass_grade.append(Stu_grade(*params_list))
        return allclass_grade

    def handle_data(self, list_data):
        '''
        清除数据中的优良中差
        :param data:传入数据
        :return: 返回的数组数据
        '''
        grade_dic = {'优': 90, '良': 80, '中': 70, '差': 60, '不及格': 0}
        for item in list_data:
            try:
                item.score = float(item.score)
            except ValueError:
                print('出现过' + item.score)
                # item.score = item.score.strip()
                if item.score in grade_dic:
                    print('true')
                    item.score = grade_dic[item.score]
                else:
                    item.score = grade_dic['不及格']

        return list_data

    def culculate_aveGPA(self, list_data):
        '''
        :return:平均绩点
        '''
        print('总课程' + str(len(list_data)))
        allnormal_scores = list()
        allabnormal_validatedscores = list()
        for index, a_item in enumerate(list_data):

            # print('sdadsad' + str(a_item.score) + 'status' + a_item.status)
            if a_item.status == '正常' and float(a_item.score) >= 60:
                # print(index)
                if len(allnormal_scores):
                    flag, *Class_index = self.find_sameCode(a_item, allnormal_scores)
                    if flag == True:
                        allnormal_scores[Class_index[0]] = a_item
                    else:
                        allnormal_scores.append(a_item)
                else:
                    allnormal_scores.append(a_item)

            elif float(a_item.score) >= 60:
                '''
                非正常且能大于60分
                就有重修和刷分，或者补考
                取的其中的最大的一次
                '''
                if len(allabnormal_validatedscores) > 0:
                    # print(index)
                    flag, *Class_index = self.find_sameCode(a_item, allabnormal_validatedscores)
                    # print('index是' + str(*index))
                    if flag:
                        allabnormal_validatedscores[Class_index[0]] = a_item
                    else:
                        # print('add')
                        allabnormal_validatedscores.append(a_item)
                else:
                    # print(index)
                    allabnormal_validatedscores.append(a_item)
        print('已经过了的课' + str(len(allnormal_scores)))
        print('重修过了的' + str(len(allabnormal_validatedscores)))
        GPA_4_totalclass = 0
        GPA_4_totalcredit = 0
        GPA_4 = 0
        all_validate_classes = allnormal_scores + allabnormal_validatedscores
        for item in all_validate_classes:
            GPA_4_totalcredit += float(item.credit)
            if item.score >= 90 and item.score < 100:
                GPA_4_totalclass += (4 * float(item.credit))
            elif item.score < 90 and item.score >= 80:
                GPA_4_totalclass += (3 * float(item.credit))
            elif item.score < 80 and item.score >= 70:
                GPA_4_totalclass += (2 * float(item.credit))
            elif item.score < 70 and item.score >= 60:
                GPA_4_totalclass += (1 * float(item.credit))
            else:
                GPA_4_totalclass += 0

            # GPA_4_total += (item.score - 50) / 10 * float(item.credit)
        GPA_4 = GPA_4_totalclass / (GPA_4_totalcredit)
        print(GPA_4)
        # for item in allabnormal_validatedscores:
        #     print(item.name+'\n'+item.code)
        return GPA_4

    def find_sameCode(self, item, array):
        '''

        :param item:item里面的code参数作为查找
        :param array: 如果array有code相同的item，那么就比较原来的item和重复的item谁的score大
        :return: 返回（是否有，被替代的索引位置）
        '''
        for a_class in array:
            '''
            已经存在了相同的课,课程编码相同
            '''
            if item.code == a_class.code:
                print('对比开始' + item.code)
                '''
                最新找的这门比之前的高
                '''
                if float(item.score) > float(a_class.score):
                    print('新的要高一点')
                    old_index = array.index(a_class)
                    return (True, old_index)

        return (False,)

    def refineData(self, list_data):
        Array_list = []
        for item in list_data:
            Array_list.append(json.dumps(item.get_json_dict()))

        return json.dumps(Array_list)

    def go(self):
        '''
        执行一次成绩页面的爬取
        '''
        data_tags = self.fetch_gradesContent()
        data = self.analysis_grades(data_tags)
        list_data = self.handle_data(data)
        GPA = self.culculate_aveGPA(list_data)
        data = self.refineData(list_data)
        return GPA, data


if __name__ == '__main__':
    # spider = GradesSpider(201505090227, 230184199707063547)
    spider = GradesSpider(201505090228, '22028319961213352X')
    spider.go()
