"""
learn flask work views
"""
# pylint: disable=invalid-name, too-few-public-methods
from flask import render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from flask_moment import Moment
from datetime import datetime
import pytz
from .. import mydb
from .forms import PayapplyForm, Paydetail
from . import work
from ..models import Payments, Approvers, User


@work.route('/payment')
@login_required
def payment():
    """payment page"""
    all_payments = Payments.query.order_by(Payments.applytime.desc()).all()

    #准备全员姓名传入视图页面
    all_users = User.query.all()
    all_users_dict = {}
    for user in all_users:
        all_users_dict[user.uid] = user.name

    return render_template('work/payment.html', paylist=all_payments, all_users_dict=all_users_dict)


@work.route('/approvelist')
@login_required
def approvelist():
    """待审批列表"""
    all_approves = Payments.query.order_by(Payments.applytime.desc()).filter_by(approveruid=current_user.uid)
    #准备全员姓名传入视图页面
    all_users = User.query.all()
    all_users_dict = {}
    for user in all_users:
        all_users_dict[user.uid] = user.name

    return render_template('work/approvelist.html', 
                           approvelist=all_approves, 
                           all_users_dict=all_users_dict)


@work.route('/paydetail/<pid>', methods=['GET', 'POST'])
@login_required
def paydetail(pid):
    """申请详情及审批操作视图"""
    #表单实例
    paydetail_app = Paydetail()

    #判断当前用户是否为审批人
    paydetail_query = Payments.query.filter_by(idpayment=pid).first()
    if current_user.uid != paydetail_query.approveruid:
        flash('你无权审批此申请.')
        return redirect(url_for('main.index'))

    #准备数据
    applier = User.query.filter_by(uid=paydetail_query.applieruid).first()
    department = Approvers.query.filter_by(idapprover=paydetail_query.dpt).first()

    #填充数据
    paydetail_app.applier_view.data = applier.name
    paydetail_app.applytime_view.data = paydetail_query.applytime
    paydetail_app.dpt_view.data = department.dpt
    paydetail_app.budgettype_view.data = paydetail_query.budgettype
    paydetail_app.amount_view.data = paydetail_query.amount
    paydetail_app.content_view.data = paydetail_query.content

    #提交审批 出问题了 不是更新 而是新增了
    if paydetail_app.validate_on_submit():
        if paydetail_app.opinion.data =="1":
            paydetail_query.opinion = True
        elif paydetail_app.opinion.data =="0":
            paydetail_query.opinion = False
        
        pytz.country_timezones('cn')
        tz = pytz.timezone('Asia/Shanghai')
        paydetail_query.approvetime = datetime.now(tz)
        mydb.session.add(paydetail_query)# pylint: disable=no-member
        mydb.session.commit()# pylint: disable=no-member 需要立刻提交数据库以获得id
        return redirect(url_for('work.approvelist'))


    return render_template('work/paydetail.html', paydetail_disp=paydetail_app)


@work.route('/payapply', methods=['GET', 'POST'])
@login_required
def payapply():
    """payment apply"""

    #表单实例
    payapplyform_app = PayapplyForm()

    #准备部门审批人列表传入视图页面
    all_approvers = Approvers.query.all()
    all_approvers_dict = {}
    for approver in all_approvers:
        approver_query = User.query.filter_by(uid=approver.approveruid).first()
        approver_name = approver_query.name
        all_approvers_dict[approver.idapprover] = approver_name

    #提交表单写入数据库
    if payapplyform_app.validate_on_submit():
        #先定位dpt对应id
        approver_selected = Approvers.query.filter_by(idapprover=payapplyform_app.dpt_apply_input.data).first()
        #调整时区
        pytz.country_timezones('cn')
        tz = pytz.timezone('Asia/Shanghai')

        newpayment = Payments(applieruid=current_user.uid,
                              applytime=datetime.now(tz),
                              dpt=payapplyform_app.dpt_apply_input.data,
                              budgettype=payapplyform_app.budgettype_apply_input.data,
                              content=payapplyform_app.content_apply_input.data,
                              amount=payapplyform_app.amount_apply_input.data,
                              approveruid=approver_selected.approveruid)
        mydb.session.add(newpayment)# pylint: disable=no-member
        mydb.session.commit()# pylint: disable=no-member 需要立刻提交数据库以获得id
        return redirect(url_for('work.payment'))

    #视图函数传入页面
    return render_template('work/payapply.html', payapplyform_display=payapplyform_app, all_approvers_dict=all_approvers_dict)

