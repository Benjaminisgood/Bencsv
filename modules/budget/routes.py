from flask import render_template, request, redirect, url_for, flash  
from flask_login import login_required, current_user  
from . import budget_bp  
from .models import BudgetRequest, Category  
from .forms import BudgetForm, CategoryForm  
from app import db  
import csv  
import io  
from flask import Response

@budget_bp.route('/submit', methods=['GET', 'POST'])  
def submit():  
    """提交报销请求（登录用户自动填写姓名，未登录者需手动填写姓名）"""  
    form = BudgetForm()  
    # 动态加载报销类别选项  
    categories = Category.query.all()  
    form.category_id.choices = [(cat.id, cat.name) for cat in categories]  
    if request.method == 'GET':  
        # 如果用户已登录，隐藏姓名字段并使用当前用户昵称  
        if current_user.is_authenticated:  
            form.name.data = current_user.username  
        return render_template('budget_submit.html', form=form)  
    # POST提交  
    if form.validate_on_submit():  
        # 检查登录状态决定使用哪个姓名  
        if current_user.is_authenticated:  
            submitter_name = current_user.username  
            user_id = current_user.id  
        else:  
            submitter_name = form.name.data  
            user_id = None  
        # 创建并保存报销请求  
        new_req = BudgetRequest(submitter_name=submitter_name,  
                                user_id=user_id,  
                                category_id=form.category_id.data,  
                                amount=float(form.amount.data),  
                                description=form.description.data,  
                                status='pending')  
        db.session.add(new_req)  
        db.session.commit()  
        flash('报销请求已提交', 'success')  
        return redirect(url_for('budget.my_requests'))  
    else:  
        # 验证失败  
        if not current_user.is_authenticated and not form.name.data:  
            flash('请填写姓名', 'danger')  
        return render_template('budget_submit.html', form=form)

@budget_bp.route('/my_requests')  
@login_required  
def my_requests():  
    """当前用户的报销请求列表"""  
    # 查询当前用户提交的所有报销请求  
    reqs = BudgetRequest.query.filter_by(user_id=current_user.id).order_by(BudgetRequest.id.desc()).all()  
    return render_template('my_requests.html', requests=reqs)

@budget_bp.route('/pending')  
@login_required  
def pending():  
    """待审批的报销请求（管理员访问）"""  
    if not current_user.is_admin:  
        flash('未授权访问', 'danger')  
        return redirect(url_for('index'))  
    # 获取所有待审批的报销请求  
    reqs = BudgetRequest.query.filter_by(status='pending').order_by(BudgetRequest.id.desc()).all()  
    return render_template('pending.html', requests=reqs)

@budget_bp.route('/approve/<int:request_id>')  
@login_required  
def approve_request(request_id):  
    """审批通过指定ID的报销请求"""  
    if not current_user.is_admin:  
        flash('未授权操作', 'danger')  
        return redirect(url_for('index'))  
    req = BudgetRequest.query.get_or_404(request_id)  
    req.status = 'approved'  
    db.session.commit()  
    flash(f'报销请求 #{request_id} 已审批通过', 'success')  
    return redirect(url_for('budget.pending'))

@budget_bp.route('/reject/<int:request_id>')  
@login_required  
def reject_request(request_id):  
    """驳回指定ID的报销请求"""  
    if not current_user.is_admin:  
        flash('未授权操作', 'danger')  
        return redirect(url_for('index'))  
    req = BudgetRequest.query.get_or_404(request_id)  
    req.status = 'rejected'  
    db.session.commit()  
    flash(f'报销请求 #{request_id} 已驳回', 'info')  
    return redirect(url_for('budget.pending'))

@budget_bp.route('/tags', methods=['GET', 'POST'])  
@login_required  
def tags():  
    """报销类别管理（管理员）"""  
    if not current_user.is_admin:  
        flash('未授权访问', 'danger')  
        return redirect(url_for('index'))  
    form = CategoryForm()  
    if form.validate_on_submit():  
        name = form.name.data.strip()  
        if name == '':  
            flash('类别名称不能为空', 'danger')  
        else:  
            # 检查重复  
            existing = Category.query.filter_by(name=name).first()  
            if existing:  
                flash('该类别已存在', 'warning')  
            else:  
                new_cat = Category(name=name)  
                db.session.add(new_cat)  
                db.session.commit()  
                flash('类别已添加', 'success')  
            return redirect(url_for('budget.tags'))  
    # GET请求或验证失败的情况  
    categories = Category.query.all()  
    return render_template('tags.html', categories=categories, form=form)

@budget_bp.route('/delete_tag/<int:cat_id>')  
@login_required  
def delete_tag(cat_id):  
    """删除报销类别（管理员）"""  
    if not current_user.is_admin:  
        flash('未授权操作', 'danger')  
        return redirect(url_for('index'))  
    cat = Category.query.get_or_404(cat_id)  
    # 如有相关的报销请求，简单处理为不允许删除  
    if cat.requests:  
        flash('存在使用该类别的报销记录，无法删除', 'danger')  
    else:  
        db.session.delete(cat)  
        db.session.commit()  
        flash('类别已删除', 'info')  
    return redirect(url_for('budget.tags'))

@budget_bp.route('/stats')  
@login_required  
def stats():  
    """报销统计图表（管理员）"""  
    if not current_user.is_admin:  
        flash('未授权访问', 'danger')  
        return redirect(url_for('index'))  
    # 汇总各类别的报销金额  
    data = (
        db.session.query(Category.name, db.func.sum(BudgetRequest.amount))
        .group_by(Category.name)
        .all()
    )
    labels = [item[0] for item in data]  
    values = [float(item[1]) if item[1] is not None else 0 for item in data]  
    return render_template('stats.html', labels=labels, values=values)

@budget_bp.route('/export')  
@login_required  
def export():  
    """导出所有报销记录为CSV（管理员）"""  
    if not current_user.is_admin:  
        flash('未授权操作', 'danger')  
        return redirect(url_for('index'))  
    output = io.StringIO()  
    writer = csv.writer(output)  
    writer.writerow(['ID', 'Submitter', 'Category', 'Amount', 'Description', 'Status'])  
    requests = BudgetRequest.query.order_by(BudgetRequest.id).all()  
    for req in requests:  
        # 查找类别名称  
        cat_name = None  
        if req.category:  
            cat_name = req.category.name  
        else:  
            cat = Category.query.get(req.category_id)  
            cat_name = cat.name if cat else ''  
        writer.writerow([req.id, req.submitter_name, cat_name, req.amount, req.description, req.status])  
    output.seek(0)  
    return Response(output.getvalue(),  
                    mimetype='text/csv',  
                    headers={"Content-Disposition": "attachment;filename=budget_requests.csv"})