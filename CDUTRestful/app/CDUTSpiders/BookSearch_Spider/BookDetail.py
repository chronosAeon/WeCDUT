class bookDetail:
    def __init__(self, Isbn = '', price='', language='', author='', publicity='', pages='', info='', brif='', book_class=''):
        '''

        :param Isbn: ISBN
        :param price:价格
        :param language:作品语种
        :param author:题名责任者
        :param publicity:出版发行
        :param pages:载体形态
        :param info:丛编
        :param brif:提要文摘
        :param book_class:中图分类
        '''
        self.Isbn = Isbn
        self.price = price
        self.language = language
        self.author = author
        self.publicity = publicity
        self.pages = pages
        self.info = info
        self.brif = brif
        self.book_class = book_class
