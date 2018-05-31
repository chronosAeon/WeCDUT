from typing import Text

from sqlalchemy import Column, Integer
from .__init__ import db


class User:
    id = Column(Integer, primary_key=True)
    open_id = Column(Text, nullable=False)
    session_id = Column(Text, nullable=False)
    token = Column(Text)
    stu_id = Column(Text)
    token_verify_time = Column(Text)
    password = Column(Text)
