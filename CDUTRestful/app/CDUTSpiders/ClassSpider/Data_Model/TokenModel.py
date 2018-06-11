from sqlalchemy import Column, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Token_model(Base):
    __tablename__ = 'token'
    __table_args__ = {"useexisting": True}
    id = Column(String(40), primary_key=True)
    token = Column(String(60))
    time = Column(String(40))
