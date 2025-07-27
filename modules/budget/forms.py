from flask_wtf import FlaskForm  
from wtforms import StringField, TextAreaField, DecimalField, SelectField, SubmitField  
from wtforms.validators import DataRequired, NumberRange

class BudgetForm(FlaskForm):  
    """报销提交表单"""  
    name = StringField('姓名', validators=[DataRequired(message="请填写姓名")])  
    category_id = SelectField('报销类别', coerce=int, validators=[DataRequired(message="请选择报销类别")])  
    amount = DecimalField('金额', places=2, validators=[DataRequired(message="请填写金额"), NumberRange(min=0.01, message="金额需大于0")])  
    description = TextAreaField('描述', validators=[DataRequired(message="请填写报销事由")])  
    submit = SubmitField('提交')

class CategoryForm(FlaskForm):  
    """报销类别表单"""  
    name = StringField('类别名称', validators=[DataRequired(message="名称不能为空")])  
    submit = SubmitField('新增类别')