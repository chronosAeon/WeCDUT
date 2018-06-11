from copy import deepcopy


class day_class(object):
    '''
    a place to store the class in a day
    '''

    def __init__(self, date, class_dic):
        self.date = date
        self.class_dic = deepcopy(class_dic)

    def convert2_dic__(self):
        return self.class_dic