import configparser

import os


class DbRMixin:
    '''
    配置文件目录固定Y:\SavvySpiderServer\CDUTSpiders\ClassSpider\setting.ini
    '''
    def __init__(self):
        pass

    @staticmethod
    def read_Dbconfig(key, section='Db_setting', path='setting.ini'):
        cfg = configparser.ConfigParser()
        config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), path)
        cfg.read(config_path)
        value = cfg.get(section, key)
        return value
