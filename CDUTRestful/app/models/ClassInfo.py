from CDUTRestful.app.models import db
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text


class ClassInfo(db.Model):
    id = Column(Integer, primary_key=True)
    current_id = Column(String(255), nullable=False)
    class_time = Column(String(255), nullable=False)
    target_id = Column(String(255), nullable=False)
    class_json = Column(Text)
    class_array_title = Column(Text)
    class_array_detail = Column(Text)

    def __init__(self, current_id, class_time, target_id, class_json, class_array_title, class_array_detail):
        self.current_id = current_id
        self.class_time = class_time
        self.target_id = target_id
        self.class_json = class_json
        self.class_array_detail = class_array_detail
        self.class_array_title = class_array_title

