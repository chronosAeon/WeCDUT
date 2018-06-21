import requests
import lxml
import re
import json
from bs4 import BeautifulSoup

from CDUTRestful.app.WeCDUT.CDUTSpider.helper.BookDetail import bookDetail


class BookDetailSpider:
    def __init__(self, url):
        self.url = url

    def get_book_item_content(self):
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
        return htmls

    def get_book_item_object(self, content):
        soup = BeautifulSoup(content, 'lxml')
        soup.encode(encoding='utf-8')
        books_name = soup.select_one('.booksCover img').attrs['title']
        trs = soup.select('.booksInfo tr')
        book_isbn, book_price, language, author, publicity, pages, info, brif, book_class = (
        '', '', '', '', '', '', '', '', '')
        for index, item in enumerate(trs):
            if index == 0:
                isbnAndPrice = trs[index].select_one('td').text
                data_array = isbnAndPrice.split(':')
                # global book_isbn, book_price
                if len(data_array) <= 1:
                    book_isbn = ''
                    book_price = data_array[0]
                else:
                    book_isbn = data_array[0]
                    book_price = data_array[1]
            if index == 1:
                language = trs[index].select_one('td').text
            if index == 3:
                author = trs[index].select_one('td').text
            if index == 4:
                publicity = trs[index].select_one('td').text
            if index == 5:
                pages = trs[index].select_one('td').text
            if index == 6:
                info = trs[index].select_one('td').text
            if index == 7:
                brif = trs[index].select_one('td').text
            if index == 11:
                book_class = trs[index].select_one('td').text
        detail_info = bookDetail(book_isbn, book_price, language, author, publicity, pages, info, brif, book_class)
        return detail_info

    def get_jsonify_item_data(self, detail_info):
        return json.dumps(detail_info.__dict__)

