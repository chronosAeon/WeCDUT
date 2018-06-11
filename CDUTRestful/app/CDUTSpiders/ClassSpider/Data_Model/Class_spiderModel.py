from sqlalchemy import Column, String, TEXT
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

'UDM = UserDataModel'


def get_UDM(table_name):
    class UDM(Base):
        __tablename__ = table_name
        __table_args__ = {"useexisting": True}
        '''
        查询者的学号作为表名
        被查询者的学号和学期号作为主键
        '''
        id = Column(String(40), primary_key=True)
        time = Column(String(40))
        json = Column(TEXT)
        class_array_title = Column(TEXT)
        class_array_detail = Column(TEXT)

    return UDM
