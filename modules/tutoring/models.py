from app import db

class TutoringRecord(db.Model):  
    """补习记录模型"""  
    __bind_key__ = 'tutoring'  
    __tablename__ = 'tutoring_record'  
    id = db.Column(db.Integer, primary_key=True)  
    submitter_name = db.Column(db.String(50))  # 提交人姓名（通常为导师）  
    user_id = db.Column(db.Integer)  # 提交人用户ID（未登录则None）  
    student_name = db.Column(db.String(50), nullable=False)  # 学生姓名  
    subject = db.Column(db.String(100), nullable=False)  # 科目/主题  
    hours = db.Column(db.Float, nullable=False)  # 补习时长  
    date = db.Column(db.Date, nullable=False)  # 补习日期  
    content = db.Column(db.Text)  # 补习内容摘要  
    feedback = db.Column(db.Text)  # 反馈（可由导师稍后填写）  
    status = db.Column(db.String(20), default='pending')  # 状态: pending/approved/rejected

    def __repr__(self):  
        return f'<TutoringRecord {self.id} {self.subject} {self.date}>'