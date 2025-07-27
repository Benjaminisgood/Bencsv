# app/__init__.py
from flask import Flask, render_template
from .config import Config
from extensions import db, login_manager
import os
from auth.models import User

def create_app():
    app = Flask(
        __name__,
        template_folder=os.path.join(os.path.dirname(os.path.dirname(__file__)), 'templates')
    )
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    # 注册蓝图
    from auth import auth_bp
    from modules.budget import budget_bp
    from modules.tutoring import tutoring_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(budget_bp)
    app.register_blueprint(tutoring_bp)

    # ✅ 添加首页路由
    @app.route('/')
    def index():
        return render_template('index.html')

    with app.app_context():
        db.create_all()

        print("Template search path:", app.jinja_loader.searchpath)

        # ✅ 自动创建管理员账户（如果不存在）
        admin_openid = "test_admin_openid"  # ➤ 自定义一个唯一标识
        admin_user = User.query.filter_by(openid=admin_openid).first()
        if not admin_user:
            admin_user = User(
                openid=admin_openid,
                username='管理员',
                is_admin=True  # ✅ 设置为管理员
            )
            db.session.add(admin_user)
            db.session.commit()
            print(f"✅ 已创建默认管理员账户 openid={admin_openid}")
        else:
            print(f"ℹ️ 管理员已存在：{admin_user.username}（openid={admin_user.openid}）")

        return app

from auth.models import User

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

