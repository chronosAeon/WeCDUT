from bs4 import BeautifulSoup

from CDUTSpiders.BookSearch_Spider.bookBrif import bookBrif
from CDUTSpiders.Class_BaseSpider.Class_BaseSpider import Class_BaseSpider
import requests
import lxml
import re
import json


class BookSearchSpider(Class_BaseSpider):
    def __init__(self, url):
        super().__init__(url)

    def Fetch_content(self):
        '''
        获取搜索的页面数据
        :return: 页面数据
        '''
        header = {

            'Host': 'www.lib.cdut.edu.cn',
            'Connection': 'keep-alive',
            'Cache-Control': 'max-age=0',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.89 Safari/537.36',
            'Upgrade-Insecure-Requests': '1',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Referer': 'http://www.lib.cdut.edu.cn/opac/search/simsearch?subtag=simsearch&tag=search',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.9',
        }

        res = requests.get(self.url, headers=header)
        res.encoding = 'utf-8'
        htmls = res.text
        # print(htmls)
        return htmls

    def get_item_lists(self, content):
        '''
        获取搜索数据并且以对象数组返回
        :return: 对象数组
        '''
        soup = BeautifulSoup(content, 'lxml')
        soup.encode(encoding='utf-8')
        Main_Slice = soup.select_one('.jp-mainCenter')
        try:
            page_text = Main_Slice.select_one('#page span').text
            page_num = re.search(r'[1-9]\d*', page_text)

            search_array = Main_Slice.select('.jp-searchList li')
            # print(len(search_array))
            """
    
                    :param detail_url:细节url
                    :param name: 书名
                    :param author: 作者
                    :param index_num: 索书号
                    :param stand_num: 标准编码
                    :param public_info: 出版信息
                    :param class_info: 分类信息
            """
            array_list = []
            for item in search_array:
                if item.select_one('h2 a'):
                    book_name = item.select_one('h2 a').text.strip()
                else:
                    book_name = ''
                if item.select_one('h2 a'):
                    book_detail_url = 'http://www.lib.cdut.edu.cn' + item.select_one('h2 a').attrs['href'].strip()
                else:
                    book_detail_url = ''
                if item.select_one('.creator'):
                    book_creator = item.select_one('.creator').text.strip()[4:].strip()
                else:
                    book_creator = ''
                if item.select_one('.call_number'):
                    index_num = item.select_one('.call_number').text[8:].strip()
                else:
                    index_num = ''
                if item.select_one('.isbn'):
                    isbn = item.select_one('.isbn').text[6:].strip()
                else:
                    isbn = ''

                if item.select_one('.publisher'):
                    public_info = item.select_one('.publisher').text.strip()
                else:
                    public_info = ''
                if item.select_one('.subject'):
                    class_info = item.select_one('.subject').text[8:].strip()
                else:
                    class_info = ''
                book_brif = bookBrif(book_detail_url, book_name, book_creator, index_num, isbn, public_info, class_info)
                array_list.append(book_brif)
                print(book_detail_url)
            return array_list
        except BaseException:
            return False

    def get_jsonify_list_data(self, array_object):
        json_array = []
        for item in array_object:
            json_array.append(json.dumps(item.__dict__))
        return json.dumps(json_array)



if __name__ == "__main__":
    URL_format = 'http://www.lib.cdut.edu.cn/opac/search?tag=search&subtag=simsearch' \
                 '&gcbook=yes&viewtype=&viewtype=&q={}&corename=' \
                 '&aliasname=%E5%85%A8%E9%83%A8%E9%A6%86%E8%97%8F&su=&library=1&library=3' \
                 '&library=4&library=5&library=6&library=7&library=8&library=9' \
                 '&library=10&library=11&library=12&library=13&field=title'
    URL = URL_format.format('哈利波特')
    spider = BookSearchSpider(URL)
    data = spider.Fetch_content()
    array_object = spider.get_item_lists(data)
    text = spider.get_jsonify_list_data(array_object)
    print(text)
    # with open('1.html', 'w', encoding='utf-8') as target:
    #     target.write(data)
