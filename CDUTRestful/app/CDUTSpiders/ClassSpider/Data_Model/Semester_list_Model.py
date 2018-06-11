from sqlalchemy import Column, String, Text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Semester_list_model(Base):
    __tablename__ = 'Semester_list'
    __table_args__ = {"useexisting": True}
    grade = Column(String(40), primary_key=True)
    list = Column(Text)
    time = Column(String(40))
