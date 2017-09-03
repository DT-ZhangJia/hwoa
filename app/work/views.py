"""
learn flask work views
"""
# pylint: disable=invalid-name, too-few-public-methods
from flask import render_template, redirect, url_for
from flask_login import login_required, current_user
from flask_moment import Moment
from datetime import datetime
from .. import mydb
from .forms import PayapplyForm


from . import work
from ..models import Payments, Approvers, User

@work.route('/payment')
@login_required
def payment():
    """payment page"""
    all_payments = Payments.query.all()
    return render_template('work/payment.html', paylist=all_payments)

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
        newpayment = Payments(applieruid=current_user.uid,
                              applytime=datetime.now(),
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

