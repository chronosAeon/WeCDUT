import json
from datetime import datetime
from CDUTRestful.app.models import db, User
from sqlalchemy import Column, Integer, String, Float, Text, DateTime


class MapInfo(db.Model):
    id = Column(Integer, primary_key=True)
    marker_latitude = Column(Float)
    marker_longitude = Column(Float)
    submit_user = Column(String(255))
    description = Column(Text)
    validate_time = Column(DateTime)

    def __init__(self, marker_latitude, marker_longitude, submit_user, description):
        self.marker_latitude = marker_latitude
        self.marker_longitude = marker_longitude
        self.submit_user = submit_user
        self.description = description
        self.validate_time = datetime.now()

    def return_back(self):
        user = User.query.filter_by(token=self.submit_user).first()
        if user:
            '''
            如果找得到用户
            '''
            if user.nick_name:
                '''
                如果用户授权了账号
                '''
                submit_user = user.nick_name

            else:
                '''
                如果用户没有授权账号
                '''
                submit_user = 'anonymous'
        else:
            '''
            如果找不到用户
            '''
            submit_user = 'anonymous'

        info_dict = {'id': self.id, 'marker_latitude': self.marker_latitude, 'marker_longittude': self.marker_longitude,
                     'submit_user': submit_user, 'description': self.description,
                     'validate_time': str(self.validate_time)}
        return json.dumps(info_dict)
