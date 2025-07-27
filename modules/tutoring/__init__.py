from flask import Blueprint  

tutoring_bp = Blueprint(
    'tutoring',
    __name__,
    url_prefix='/tutoring',
    template_folder='templates'  # 相对路径：modules/tutoring/templates/
)
from . import routes  # 导入路由定义