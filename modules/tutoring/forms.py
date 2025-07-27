from flask_wtf import FlaskForm  
from wtforms import StringField, TextAreaField, DecimalField, DateField, SubmitField  
from wtforms.validators import DataRequired, NumberRange

class TutoringForm(FlaskForm):  
    """补习记录提交表单"""  
    name = StringField('姓名', validators=[DataRequired(message="请填写导师姓名")])  
    student_name = StringField('学生姓名', validators=[DataRequired(message="请填写学生姓名")])  
    subject = StringField('科目/主题', validators=[DataRequired(message="请填写科目或主题")])  
    hours = DecimalField('时长(小时)', places=1, validators=[DataRequired(message="请填写时长"), NumberRange(min=0.1, message="时长必须大于0")])  
    date = DateField('日期', format='%Y-%m-%d', validators=[DataRequired(message="请选择日期")])  
    content = TextAreaField('内容摘要', validators=[DataRequired(message="请填写内容摘要")])  
    submit = SubmitField('提交')

class FeedbackForm(FlaskForm):  
    """补习反馈表单"""  
    feedback = TextAreaField('反馈', validators=[DataRequired(message="反馈不能为空")])  
    submit = SubmitField('提交反馈')