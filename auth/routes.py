# auth/routes.py
import requests
from flask import redirect, request, url_for, flash, current_app
from flask_login import login_user, logout_user, current_user
from extensions import db
from auth import auth_bp
from auth.models import User

@auth_bp.route('/login')
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    appid = current_app.config['WECHAT_APPID']
    redirect_uri = current_app.config['WECHAT_REDIRECT_URI']
    wechat_auth_url = (
        f"https://open.weixin.qq.com/connect/qrconnect?appid={appid}"
        f"&redirect_uri={redirect_uri}"
        f"&response_type=code&scope=snsapi_login&state=xyz#wechat_redirect"
    )
    return redirect(wechat_auth_url)

@auth_bp.route('/callback')
def wechat_callback():
    code = request.args.get('code')
    state = request.args.get('state')
    if not code:
        flash('微信登录失败：未获取code', 'danger')
        return redirect(url_for('index'))

    appid = current_app.config['WECHAT_APPID']
    secret = current_app.config['WECHAT_SECRET']
    token_url = "https://api.weixin.qq.com/sns/oauth2/access_token"
    params = {
        'appid': appid,
        'secret': secret,
        'code': code,
        'grant_type': 'authorization_code'
    }
    try:
        token_resp = requests.get(token_url, params=params, timeout=5)
        token_data = token_resp.json()
    except Exception:
        flash('微信登录失败：请求异常', 'danger')
        return redirect(url_for('index'))

    openid = token_data.get('openid')
    access_token = token_data.get('access_token')
    if not openid or not access_token:
        flash('微信登录失败：响应不包含openid', 'danger')
        return redirect(url_for('index'))

    info_url = "https://api.weixin.qq.com/sns/userinfo"
    info_params = {
        'access_token': access_token,
        'openid': openid,
        'lang': 'zh_CN'
    }
    try:
        info_resp = requests.get(info_url, params=info_params, timeout=5)
        info_data = info_resp.json()
    except Exception:
        info_data = {}

    nickname = info_data.get('nickname', '微信用户')
    user = User.query.filter_by(openid=openid).first()
    if not user:
        user = User(openid=openid, username=nickname)
        db.session.add(user)
        db.session.commit()

    login_user(user)
    flash('微信登录成功', 'success')
    return redirect(url_for('index'))

@auth_bp.route('/logout')
def logout():
    logout_user()
    flash('您已退出登录', 'info')
    return redirect(url_for('index'))

# auth/routes.py
from flask import render_template, request, abort

@auth_bp.route('/local_login', methods=['GET', 'POST'])
def local_login():
    if request.remote_addr != '127.0.0.1':
        abort(403)
        
    if request.method == 'POST':
        openid = request.form.get('openid')
        nickname = request.form.get('nickname') or '开发者'
        if not openid:
            flash('请输入 OpenID', 'warning')
            return redirect(url_for('auth.local_login'))

        user = User.query.filter_by(openid=openid).first()
        if not user:
            user = User(openid=openid, username=nickname)
            if openid == current_app.config.get('ADMIN_OPENID'):
                user.is_admin = True
            db.session.add(user)
            db.session.commit()

        login_user(user)
        flash('本地登录成功', 'info')
        return redirect(url_for('index'))

    return render_template('local_login.html')