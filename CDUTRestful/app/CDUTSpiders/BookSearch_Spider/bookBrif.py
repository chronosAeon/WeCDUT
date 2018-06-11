class bookBrif:
    def __init__(self, detail_url, name, author, index_num, stand_num, public_info, class_info):
        """

        :param detail_url:细节url
        :param name: 书名
        :param author: 作者
        :param index_num: 索书号
        :param stand_num: 标准编码
        :param public_info: 出版信息
        :param class_info: 分类信息
        """
        self.detail_url = detail_url
        self.name = name
        self.author = author
        self.index_num = index_num
        self.stand_num = stand_num
        self.public_info = public_info
        self.class_info = class_info
