"""
合同视图模块
"""
# pylint: disable=invalid-name, too-few-public-methods
from datetime import datetime
from flask import render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from flask_moment import Moment
import pytz
from sqlalchemy import and_
from .. import mydb
from .forms import LabelDict, PayapplyForm, Paydetail, AddPermissionForm, \
    Permissiondetail, ContractApplyForm
from . import work
from ..models import Payments, Approvers, User, Permissions, Departments, Operations, Contracts



@work.route('/contractapply', methods=['GET', 'POST'])
@login_required
def contractapply():
    """contractapply apply"""

    #表单实例
    contractapply_app = ContractApplyForm()

    #调整时区
    pytz.country_timezones('cn')
    tz = pytz.timezone('Asia/Shanghai')

    """
    各种判断
    1.（超部门长限额 and 申请人不是部门长） or （未超部门长限额 and 申请人是部门长）== 不能申请
    2.是否需要交叉复核？根据事项区分，赋值状态字段不同位值【先设置采购大件直接跳过cv】
    3.超部门长限额 and 申请人是部门长 == 一级复核设为董事长 【这项判断交给列表处理】
    （暂缓）4.是否有二级复核的抽样(3=False)
    """

    if contractapply_app.validate_on_submit():
        operation = Operations.query.filter_by(idoperations=contractapply_app.contracttype_apply_input.data).first()# pylint: disable=C0301
        opcode = operation.opapprvcode
        dptoplimit = Permissions.query.order_by(eval("Permissions." + opcode + ".desc()")).filter( \
            and_(Permissions.companyid == contractapply_app.company_apply_input.data, \
            Permissions.positionid == contractapply_app.applydpt_apply_input.data, \
            Permissions.termstart < datetime.now(tz), Permissions.termend > datetime.now(tz), \
            Permissions.approved == True, Permissions.valid == True)).first()

        incharge = Permissions.query.filter(and_( \
            Permissions.companyid == contractapply_app.company_apply_input.data, \
            Permissions.positionid == contractapply_app.applydpt_apply_input.data, \
            Permissions.termstart < datetime.now(tz), \
            Permissions.termend > datetime.now(tz), Permissions.approved == True, \
            Permissions.valid == True)).all()
        inchargelist = []
        for user in incharge:
            inchargelist.append(user.puid)

        #如果业务金额超过本部门部门长权限，申请人又不是部门长的话就无法提交。
        if eval("dptoplimit."+opcode) < float(contractapply_app.amount_apply_input.data) and \
            current_user.uid not in inchargelist:
            flash('您无法申请超限额合同，请让本部门负责人提交申请。')
        #如果业务金额未超过本部门部门长权限，申请人又是部门长的话就无法提交。
        elif eval("dptoplimit."+opcode) >= float(contractapply_app.amount_apply_input.data) and \
            current_user.uid in inchargelist:
            flash('您作为本部门负责人，不可自行提交申请。')
        else:
            newcontract = Contracts(companyid=contractapply_app.company_apply_input.data,
                                    applieruid=current_user.uid,
                                    applydpt=contractapply_app.applydpt_apply_input.data,
                                    applytime=datetime.now(tz),
                                    opcode=operation.opcode,
                                    content=contractapply_app.content_apply_input.data,
                                    amount=contractapply_app.amount_apply_input.data)
            mydb.session.add(newcontract)# pylint: disable=no-member
            mydb.session.commit()# pylint: disable=no-member
            flash('提交成功。')
            return redirect(url_for('work.allcontractlist'))


    return render_template('work/contractapply.html', contractapply_display=contractapply_app)


@work.route('/allcontractlist')
@login_required
def allcontractlist():
    """全部合同列表"""

    allcontract = Contracts.query.order_by(Contracts.applytime.desc()).all()
    label_dict = LabelDict()

    return render_template('work/allcontractlist.html',
                           allcontract=allcontract, label_dict=label_dict)
