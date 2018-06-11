class Stu_grade:
    def __init__(self, term, code, name, teacher, credit, score, status, GPA_point, in_store_person, time):
        self.term = term
        self.code = code
        self.name = name
        self.teacher = teacher
        self.credit = credit
        self.score = score
        self.status = status
        self.GPA_point = GPA_point
        self.in_store_person = in_store_person
        self.time = time

    def get_json_dict(self):
        self_dict = {'name': self.name, 'credit': self.credit, 'score': self.score, 'status': self.status}
        return self_dict
