import json

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import time as time_module
from CDUTSpiders.Class_BaseSpider.Class_BaseSpider import Class_BaseSpider
from bs4 import BeautifulSoup
import re
import chardet

ANNOUNCE_URL = r'http://www.cdut.edu.cn/xww/type/1000020104.html'
ACADEMY_URL = r'http://www.cdut.edu.cn/xww/type/1000020107.html'
QUICK_INFO_URL = r'http://www.cdut.edu.cn/xww/type/1000020102.html'
JOURNAL_URL = r'http://www.cdut.edu.cn/xww/typePage.do?yygrlxym=null&lmdm=1000020114&kjdm='


class InformData:
    def __init__(self, url, brif, time):
        self.url = url
        self.brif = brif
        self.time = time


class InformSpider(Class_BaseSpider):
    def __init__(self, url):
        self.driver = webdriver.PhantomJS(executable_path=r'/data/PhantomJS/phantomjs-2.1.1-linux-x86_64/bin/phantomjs')
        # self.driver = driver_instance
        self.driver.implicitly_wait(30)
        super(InformSpider, self).__init__(url)

    def fetch_content(self):
        '''
        目前只有QUICK_INFO_URL，JOURNAL_URL能被响应
        :return:
        '''
        self.driver.get(self.url)
        content = self.driver.page_source
        # time_module.sleep(4)
        data_text = re.findall(r'<div id="showhtml.*</ul></div>', content)
        print(content)
        if len(data_text) > 0:
            code = data_text[0].encode('UTF-8')

            print(code)
            soup = BeautifulSoup(code, 'lxml')
            '#showhtml > ul'
            '#showhtml > ul > li:nth-child(1)'
            ul = soup.select_one('#showhtml > ul')
            # if ul.select('li') is None:
            li_array = ul.select('li')
            data_array = []
            for item in li_array:
                a_flag = item.find('a')
                url = a_flag.attrs['href']
                brif = a_flag.attrs['xwbt']
                if item.select_one('.time') is None:
                    time = ''
                else:
                    time = item.select_one('.time').text
                # print(time)
                data_array.append(InformData(url, brif, time))
            # print(data_array)
            return data_array
        else:
            return False

    def jsonify_data(self, array_object):
        if array_object:
            jsonified_data = []
            for item in array_object:
                item_jsonified_data = json.dumps(item.__dict__)
                jsonified_data.append(item_jsonified_data)
            return json.dumps(jsonified_data)
        else:
            return False

    def go(self):
        print('start get info')
        data_array = self.fetch_content()
        print('finish info')
        self.driver.close()
        return self.jsonify_data(data_array)


if __name__ == "__main__":
    # print('start get info')
    # URL = 'http://www.cdut.edu.cn/xww/type/1000020102.html'
    # URL = 'http://www.cdut.edu.cn/xww/type/1000020104.html'
    # URL = 'http://www.cdut.edu.cn/xww/typePage.do?yygrlxym=null&lmdm=1000020104&kjdm='
    driver = webdriver.PhantomJS(executable_path=r'Y:\phantomJs\phantomjs-2.1.1-windows\bin\phantomjs.exe')
    driver.get(ACADEMY_URL)
    content = driver.page_source
    print(content)
    driver.get(JOURNAL_URL)
    content = driver.page_source
    print(content)
    # spider = InformSpider(JOURNAL_URL, driver)
    # print(spider.go())
    # spider.fetch_content()
