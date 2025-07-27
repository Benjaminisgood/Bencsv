from flask import render_template, request, redirect, url_for, flash  
from flask_login import login_required, current_user  
from . import tutoring_bp  
from .models import TutoringRecord  
from .forms import TutoringForm, FeedbackForm  
from app import db  
import csv  
import io  
from flask import Response  
from datetime import datetime

@tutoring_bp.route('/submit', methods=['GET', 'POST'])  
def submit():  
    """提交补习记录"""  
    form = TutoringForm()  
    if request.method == 'GET':  
        # 如已登录，填充导师姓名  
        if current_user.is_authenticated:  
            form.name.data = current_user.username  
        return render_template('tutoring_submit.html', form=form)  
    if form.validate_on_submit():  
        # 确定提交者信息  
        if current_user.is_authenticated:  
            submitter_name = current_user.username  
            user_id = current_user.id  
        else:  
            submitter_name = form.name.data  
            user_id = None  
        new_rec = TutoringRecord(  
            submitter_name=submitter_name,  
            user_id=user_id,  
            student_name=form.student_name.data,  
            subject=form.subject.data,  
            hours=float(form.hours.data),  
            date=form.date.data,  
            content=form.content.data,  
            feedback=None,  
            status='pending'  
        )  
        db.session.add(new_rec)  
        db.session.commit()  
        flash('补习记录已提交', 'success')  
        return redirect(url_for('tutoring.my_records'))  
    else:  
        if not current_user.is_authenticated and not form.name.data:  
            flash('请填写导师姓名', 'danger')  
        return render_template('tutoring_submit.html', form=form)

@tutoring_bp.route('/feedback/<int:record_id>', methods=['GET', 'POST'])  
@login_required  
def feedback(record_id):  
    """填写补习反馈"""  
    rec = TutoringRecord.query.get_or_404(record_id)  
    # 权限：只有创建者或管理员可以填写反馈  
    if current_user.id != rec.user_id and not current_user.is_admin:  
        flash('未授权访问该记录', 'danger')  
        return redirect(url_for('index'))  
    form = FeedbackForm()  
    if request.method == 'GET':  
        return render_template('feedback.html', record=rec, form=form)  
    if form.validate_on_submit():  
        rec.feedback = form.feedback.data  
        db.session.commit()  
        flash('反馈已提交', 'success')  
        return redirect(url_for('tutoring.my_records'))  
    return render_template('feedback.html', record=rec, form=form)

@tutoring_bp.route('/my_records')  
@login_required  
def my_records():  
    """当前用户提交的补习记录"""  
    recs = TutoringRecord.query.filter_by(user_id=current_user.id).order_by(TutoringRecord.id.desc()).all()  
    return render_template('my_records.html', records=recs)

@tutoring_bp.route('/admin_pending')  
@login_required  
def admin_pending():  
    """待审核的补习记录（管理员）"""  
    if not current_user.is_admin:  
        flash('未授权访问', 'danger')  
        return redirect(url_for('index'))  
    recs = TutoringRecord.query.filter_by(status='pending').order_by(TutoringRecord.id.desc()).all()  
    return render_template('admin_pending.html', records=recs)

@tutoring_bp.route('/approve/<int:record_id>')  
@login_required  
def approve_record(record_id):  
    """审核通过补习记录"""  
    if not current_user.is_admin:  
        flash('未授权操作', 'danger')  
        return redirect(url_for('index'))  
    rec = TutoringRecord.query.get_or_404(record_id)  
    rec.status = 'approved'  
    db.session.commit()  
    flash(f'补习记录 #{record_id} 已批准', 'success')  
    return redirect(url_for('tutoring.admin_pending'))

@tutoring_bp.route('/reject/<int:record_id>')  
@login_required  
def reject_record(record_id):  
    """审核驳回补习记录"""  
    if not current_user.is_admin:  
        flash('未授权操作', 'danger')  
        return redirect(url_for('index'))  
    rec = TutoringRecord.query.get_or_404(record_id)  
    rec.status = 'rejected'  
    db.session.commit()  
    flash(f'补习记录 #{record_id} 已驳回', 'info')  
    return redirect(url_for('tutoring.admin_pending'))

@tutoring_bp.route('/all_records')  
@login_required  
def all_records():  
    """所有补习记录列表（管理员）"""  
    if not current_user.is_admin:  
        flash('未授权访问', 'danger')  
        return redirect(url_for('index'))  
    recs = TutoringRecord.query.order_by(TutoringRecord.id.desc()).all()  
    return render_template('all_records.html', records=recs)

@tutoring_bp.route('/export')  
@login_required  
def export():  
    """导出所有补习记录为CSV（管理员）"""  
    if not current_user.is_admin:  
        flash('未授权操作', 'danger')  
        return redirect(url_for('index'))  
    output = io.StringIO()  
    writer = csv.writer(output)  
    writer.writerow(['ID', 'Tutor', 'Student', 'Subject', 'Hours', 'Date', 'Content', 'Feedback', 'Status'])  
    recs = TutoringRecord.query.order_by(TutoringRecord.id).all()  
    for rec in recs:  
        writer.writerow([  
            rec.id,  
            rec.submitter_name,  
            rec.student_name,  
            rec.subject,  
            rec.hours,  
            rec.date.strftime('%Y-%m-%d'),  
            rec.content,  
            rec.feedback or '',  
            rec.status  
        ])  
    output.seek(0)  
    return Response(output.getvalue(),  
                    mimetype='text/csv',  
                    headers={"Content-Disposition": "attachment;filename=tutoring_records.csv"})