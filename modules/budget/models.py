from app import db

class Category(db.Model):  
    """报销类别模型"""  
    __bind_key__ = 'budget'  
    __tablename__ = 'category'  
    id = db.Column(db.Integer, primary_key=True)  
    name = db.Column(db.String(50), unique=True, nullable=False)

    def __repr__(self):  
        return f'<Category {self.name}>'

class BudgetRequest(db.Model):  
    """报销请求模型"""  
    __bind_key__ = 'budget'  
    __tablename__ = 'budget_request'  
    id = db.Column(db.Integer, primary_key=True)  
    submitter_name = db.Column(db.String(50))  # 提交人姓名（游客填写或登录用户昵称）  
    user_id = db.Column(db.Integer)  # 提交人用户ID（未登录则为None）  
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))  
    amount = db.Column(db.Float, nullable=False)  # 报销金额  
    description = db.Column(db.Text, nullable=False)  # 描述/备注  
    status = db.Column(db.String(20), default='pending')  # 状态: pending/approved/rejected  
    category = db.relationship('Category', backref='requests')

    def __repr__(self):  
        return f'<BudgetRequest {self.id} {self.category_id} {self.amount}>'