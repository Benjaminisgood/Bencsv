class Config:  
    # 数据库URI配置：主数据库用于用户，绑定数据库用于各模块  
    SQLALCHEMY_DATABASE_URI = 'sqlite:///auth.db'  # 主SQLite数据库URI，用于User模型等  
    SQLALCHEMY_BINDS = {  
        'budget': 'sqlite:///budget.db',     # 报销模块数据库  
        'tutoring': 'sqlite:///tutoring.db'  # 补习模块数据库  
    }  
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # 关闭修改跟踪  
    SECRET_KEY = 'replace_with_random_secret'  # Flask-WTF CSRF需要的密钥  
    # 微信OAuth登录的凭证配置  
    WECHAT_APPID = 'your_wechat_appid'  
    WECHAT_SECRET = 'your_wechat_secret'  
    WECHAT_REDIRECT_URI = 'http://yourdomain.com/auth/callback'

    DEBUG = True  # 设置为 False 后 /local_login 页面就不再可访问
    ADMIN_OPENID = 'benbenben'