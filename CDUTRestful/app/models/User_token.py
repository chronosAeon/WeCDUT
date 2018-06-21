from sqlalchemy import Column, String, Integer, DateTime

from CDUTRestful.app.models import db


class User_token(db.Model):
    id = Column(Integer, primary_key=True)
    stu_id = Column(String(255))
    class_token = Column(String(255))
    generate_time = Column(DateTime)

    def __init__(self, stu_id, class_token, generate_time):
        self.stu_id = stu_id
        self.class_token = class_token
        self.generate_time = generate_time
