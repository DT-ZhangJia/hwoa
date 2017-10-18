"""
合同视图模块
"""
# pylint: disable=invalid-name, too-few-public-methods
from datetime import datetime
from flask import render_template, redirect, url_for, flash, make_response
from flask_login import login_required, current_user
from flask_moment import Moment
import pytz
from sqlalchemy import and_, or_, not_
from .. import mydb
from .forms import LabelDict, PayapplyForm, Paydetail, AddPermissionForm, \
    Permissiondetail, ContractApplyForm, ContractCVForm, ContractLawForm, ContractAccForm, \
    ContractDPTForm, ContractViewForm, ViewPDF
from . import work
from ..models import Payments, Approvers, User, Permissions, Departments, \
    Operations, Contracts, Crossvalids, Lawyers
import pdfkit
#from io import BytesIO


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

        if dptoplimit is not None:
            #如果业务金额超过本部门部门长权限，申请人又不是部门长的话就无法提交。
            if eval("dptoplimit."+opcode) < float(contractapply_app.amount_apply_input.data) and \
                current_user.uid not in inchargelist:
                flash('您无法申请超限额合同，请让本部门负责人提交申请。')
            #如果业务金额未超过本部门部门长权限，申请人又是部门长的话就无法提交。
            elif eval("dptoplimit."+opcode) >= float(contractapply_app.amount_apply_input.data) and\
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
                #提交时根据是否为原辅料或者固定资产采购合同决定是否需要交叉复核
                if int(contractapply_app.contracttype_apply_input.data) in [5, 8]:
                    newcontract = Contracts(companyid=contractapply_app.company_apply_input.data,
                                            applieruid=current_user.uid,
                                            applydpt=contractapply_app.applydpt_apply_input.data,
                                            applytime=datetime.now(tz),
                                            opcode=operation.opcode,
                                            content=contractapply_app.content_apply_input.data,
                                            amount=contractapply_app.amount_apply_input.data,
                                            procedure=0b1)
                else:
                    newcontract = Contracts(companyid=contractapply_app.company_apply_input.data,
                                            applieruid=current_user.uid,
                                            applydpt=contractapply_app.applydpt_apply_input.data,
                                            applytime=datetime.now(tz),
                                            opcode=operation.opcode,
                                            content=contractapply_app.content_apply_input.data,
                                            amount=contractapply_app.amount_apply_input.data,
                                            procedure=0b100)
                mydb.session.add(newcontract)# pylint: disable=no-member
                mydb.session.commit()# pylint: disable=no-member
                #flash('提交成功。')
            return redirect(url_for('work.allcontractlist'))
        else:
            flash('本部门尚未设置部门负责人，暂不可提交申请。')


    return render_template('work/contractapply.html', contractapply_display=contractapply_app)


@work.route('/allcontractlist')
@login_required
def allcontractlist():
    """全部合同列表"""

    allcontract = Contracts.query.order_by(Contracts.applytime.desc()).all()
    label_dict = LabelDict()

    return render_template('work/allcontractlist.html',
                           allcontract=allcontract, label_dict=label_dict)



@work.route('/contractview/<contractid>', methods=['GET', 'POST'])
@login_required
def contractview(contractid):
    """合同审批详情页面"""

    contractviewform_app = ContractViewForm()
    label_dict = LabelDict()
    contract = Contracts.query.filter_by(idcontracts=contractid).first()
    operation = Operations.query.filter_by(opcode=contract.opcode).first()# pylint: disable=C0301

    if contract is not None:

        #填充数据
        contractviewform_app.company_view_input.data = label_dict.all_company_dict[contract.companyid] # pylint: disable=C0301
        contractviewform_app.applydpt_view_input.data = label_dict.all_dpt_dict[contract.applydpt]
        contractviewform_app.contracttype_view_input.data = operation.opname
        contractviewform_app.content_view_input.data = contract.content
        contractviewform_app.amount_view_input.data = contract.amount
        contractviewform_app.applier_view_input.data = label_dict.all_users_dict[contract.applieruid] # pylint: disable=C0301
        contractviewform_app.applytime_view_input.data = contract.applytime

        if contract.crossuid is None:
            contractviewform_app.cvuser_view_input.data = ""
        else:
            contractviewform_app.cvuser_view_input.data = label_dict.all_users_dict[contract.crossuid] # pylint: disable=C0301
        if contract.procedure|0b1111111110 == 0b1111111111:
            contractviewform_app.cvcontent_view_input.data = "[系统提示]具有前置流程的申请无需交叉复核。前置流程完整性暂须财务复核确认。" # pylint: disable=C0301
        elif contract.procedure|0b1111111100 == 0b1111111111:
            contractviewform_app.cvcontent_view_input.data = "[系统提示]具有前置流程的申请无需交叉复核。前置流程完整性已经财务复核确认。" # pylint: disable=C0301
        elif contract.crosscontent is None:
            contractviewform_app.cvcontent_view_input.data = ""
        else:
            contractviewform_app.cvcontent_view_input.data = contract.crosscontent
        if contract.crossopinion is None:
            contractviewform_app.cvopinion_view_input.data = ""
        else:
            contractviewform_app.cvopinion_view_input.data = {True:"有异议",False:"无异议"}[contract.crossopinion] # pylint: disable=C0301
        if contract.crosstime is None:
            contractviewform_app.cvtime_view_input.data = ""
        else:
            contractviewform_app.cvtime_view_input.data = contract.crosstime
        #lawyer
        if contract.lawyeruid is None:
            contractviewform_app.lawyer_view_input.data = ""
        else:
            contractviewform_app.lawyer_view_input.data = label_dict.all_users_dict[contract.lawyeruid]
        if contract.lawyercontent is None:
            contractviewform_app.lawcontent_view_input.data = ""
        else:
            contractviewform_app.lawcontent_view_input.data = contract.lawyercontent
        if contract.lawyeropinion is None:
            contractviewform_app.lawopinion_view_input.data = ""
        else:
            contractviewform_app.lawopinion_view_input.data = {True:"有异议",False:"无异议"}[contract.lawyeropinion]
        if contract.lawyertime is None:
            contractviewform_app.lawyertime_view_input.data = ""
        else:
            contractviewform_app.lawyertime_view_input.data = contract.lawyertime
        #acc
        if contract.accuid is None:
            contractviewform_app.acc_view_input.data = ""
        else:
            contractviewform_app.acc_view_input.data = label_dict.all_users_dict[contract.accuid]
        if contract.acccontent is None:
            contractviewform_app.acccontent_view_input.data = ""
        else:
            contractviewform_app.acccontent_view_input.data = contract.acccontent
        if contract.accopinion is None:
            contractviewform_app.accopinion_view_input.data = ""
        else:
            contractviewform_app.accopinion_view_input.data = {True:"有异议",False:"无异议"}[contract.accopinion]
        if contract.acctime is None:
            contractviewform_app.acctime_view_input.data = ""
        else:
            contractviewform_app.acctime_view_input.data = contract.acctime
        #incharge
        if contract.authid is None:
            contractviewform_app.auth_view_input.data = ""
        else:
            contractviewform_app.auth_view_input.data = "[授权书] " + str(contract.authid) + " 号"
        if contract.approveruid is None:
            contractviewform_app.approver_view_input.data = ""
        else:
            contractviewform_app.approver_view_input.data = label_dict.all_users_dict[contract.approveruid]
        if contract.apprvopinion is None:
            contractviewform_app.apprvopinion_view_input.data = ""
        else:
            contractviewform_app.apprvopinion_view_input.data = {True:"同意",False:"不同意"}[contract.apprvopinion]
        contractviewform_app.apprvtime_view_input.data = contract.apprvtime




    else:
        return render_template('404.html'), 404

    viewpdf = ViewPDF()
    if viewpdf.is_submitted():
        htmlfile = render_template('work/contractpdf.html', pdfdata=contractviewform_app, label_dict=label_dict, contractid=contractid)
        pdffile = pdfkit.from_string(htmlfile,False)
        response = make_response(pdffile)
        response.headers['Content-Type'] = 'aplication/pdf'
        response.headers['Content-Disposition'] = 'attachment; filename=contract_'+contractid+'.pdf'
        return response
    

    return render_template('work/contractview.html', contractviewform_disp=contractviewform_app,
                           viewpdf=viewpdf, label_dict=label_dict)



@work.route('/contractoncv/<contractid>', methods=['GET', 'POST'])
@login_required
def contractoncv(contractid):
    """交叉复核页面"""

    #调整时区
    pytz.country_timezones('cn')
    tz = pytz.timezone('Asia/Shanghai')
    label_dict = LabelDict()

    contract = Contracts.query.filter_by(idcontracts=contractid).first()
    if contract is not None:

        operation = Operations.query.filter_by(opcode=contract.opcode).first()# pylint: disable=C0301

        #如果此合同的状态值第一位是1的话，无需交叉复核。
        if contract.procedure|0b1111111110 == 0b1111111111:
            flash("本合同无需交叉复核。")
            return redirect(url_for('work.addrules'))
        #如果第四位是1的话，表示已经交叉复核完毕。
        elif contract.procedure|0b1111110111 == 0b1111111111:
            flash("本合同已经过交叉复核。")
            return redirect(url_for('work.addrules'))

        #判断当前用户是否无部门长、董事长权限，且有权限进行交叉复核，且不等于applier
        #对应部门长及董事长
        inchargetest = Permissions.query.filter(or_(\
            and_(Permissions.puid == current_user.uid, \
            Permissions.companyid == contract.companyid, \
            Permissions.positionid == 2, Permissions.termstart <= datetime.now(tz), \
            Permissions.termend >= datetime.now(tz), Permissions.valid == True),\
            and_(Permissions.puid == current_user.uid, \
            Permissions.companyid == contract.companyid, \
            Permissions.positionid == contract.applydpt, Permissions.termstart <= datetime.now(tz),\
            Permissions.termend >= datetime.now(tz), Permissions.valid == True))).first()
        #对应部门交叉复核人
        crosstest = Crossvalids.query.filter(and_(Crossvalids.companyid == contract.companyid,\
            Crossvalids.crossdpt == contract.applydpt, \
            Crossvalids.crossuid == current_user.uid)).first()
        if crosstest is None:
            flash("您无此部门业务交叉复核权限。")
            return redirect(url_for('work.addrules'))
        elif (inchargetest is not None) or (contract.applieruid == current_user.uid):
            flash("您有与交叉复核不相容的权限或角色。")
            return redirect(url_for('work.addrules'))


        #填充表单数据
        contractcvform_app = ContractCVForm()
        contractcvform_app.company_cv_input.data = label_dict.all_company_dict[contract.companyid]
        contractcvform_app.applydpt_cv_input.data = label_dict.all_dpt_dict[contract.applydpt]
        contractcvform_app.contracttype_cv_input.data = operation.opname
        contractcvform_app.content_cv_input.data = contract.content
        contractcvform_app.amount_cv_input.data = contract.amount
        contractcvform_app.applier_cv_input.data = label_dict.all_users_dict[contract.applieruid]
        contractcvform_app.applytime_cv_input.data = contract.applytime
        if contract.lawyeruid is None:
            contractcvform_app.lawyer_cv_input.data = ""
        else:
            contractcvform_app.lawyer_cv_input.data = label_dict.all_users_dict[contract.lawyeruid]
        contractcvform_app.lawcontent_cv_input.data = contract.lawyercontent
        if contract.lawyeropinion is None:
            contractcvform_app.lawopinion_cv_input.data = ""
        else:
            contractcvform_app.lawopinion_cv_input.data = {True:"有异议",False:"无异议"}[contract.lawyeropinion] # pylint: disable=C0301
        contractcvform_app.lawyertime_cv_input.data = contract.lawyertime
        if contract.accuid is None:
            contractcvform_app.acc_cv_input.data = ""
        else:
            contractcvform_app.acc_cv_input.data = label_dict.all_users_dict[contract.accuid]
        contractcvform_app.acccontent_cv_input.data = contract.acccontent
        if contract.accopinion is None:
            contractcvform_app.accopinion_cv_input.data = ""
        else:
            contractcvform_app.accopinion_cv_input.data = {True:"有异议",False:"无异议"}[contract.accopinion]
        contractcvform_app.acctime_cv_input.data = contract.acctime

    else:
        return render_template('404.html'), 404


    if contractcvform_app.validate_on_submit():
        if contract.procedure|0b1111110111 == 0b1111111111:
            flash("本合同已经过交叉复核，请不要重复提交。")
            return redirect(url_for('work.addrules'))

        if contractcvform_app.cvopinion_cv_input.data == "0":
            contract.crossopinion = False
        elif contractcvform_app.cvopinion_cv_input.data == "1":
            contract.crossopinion = True

        contract.procedure = contract.procedure|0b1000
        contract.crossuid = current_user.uid
        contract.crosscontent = contractcvform_app.cvcontent_cv_input.data
        contract.crosstime = datetime.now(tz)
        mydb.session.add(contract)# pylint: disable=no-member
        mydb.session.commit()# pylint: disable=no-member

        return redirect(url_for('work.contractreview'))


    return render_template('work/contractoncv.html', contractcvform_disp=contractcvform_app,
                           contract=contract, label_dict=label_dict)



@work.route('/contractonlaw/<contractid>', methods=['GET', 'POST'])
@login_required
def contractonlaw(contractid):
    """法务复核页面"""

    #调整时区
    pytz.country_timezones('cn')
    tz = pytz.timezone('Asia/Shanghai')
    label_dict = LabelDict()

    contract = Contracts.query.filter_by(idcontracts=contractid).first()
    if contract is not None:

        operation = Operations.query.filter_by(opcode=contract.opcode).first()# pylint: disable=C0301

        #如果第五位是1的话，表示已经法务复核完毕。
        if contract.procedure|0b1111101111 == 0b1111111111:
            flash("本合同已经过法务复核。")
            return redirect(url_for('work.addrules'))

        #判断当前用户是否无部门长、董事长权限，且有权限进行法务复核，且不等于applier
        #对应部门长及董事长
        inchargetest = Permissions.query.filter(or_(\
            and_(Permissions.puid == current_user.uid, \
            Permissions.companyid == contract.companyid, \
            Permissions.positionid == 2, Permissions.termstart <= datetime.now(tz), \
            Permissions.termend >= datetime.now(tz), Permissions.valid == True),\
            and_(Permissions.puid == current_user.uid, \
            Permissions.companyid == contract.companyid, \
            Permissions.positionid == contract.applydpt, Permissions.termstart <= datetime.now(tz),\
            Permissions.termend >= datetime.now(tz), Permissions.valid == True))).first()
        #法务复核人
        lawtest = Lawyers.query.filter(and_(Lawyers.companyid == contract.companyid,\
            Lawyers.consultant == 1, \
            Lawyers.consultantuid == current_user.uid)).first()
        if lawtest is None:
            flash("您无法务复核权限。")
            return redirect(url_for('work.addrules'))
        elif (inchargetest is not None) or (contract.applieruid == current_user.uid):
            flash("您有与法务复核不相容的权限或角色。")
            return redirect(url_for('work.addrules'))


        #填充表单数据
        contractlawform_app = ContractLawForm()
        contractlawform_app.company_law_input.data = label_dict.all_company_dict[contract.companyid]
        contractlawform_app.applydpt_law_input.data = label_dict.all_dpt_dict[contract.applydpt]
        contractlawform_app.contracttype_law_input.data = operation.opname
        contractlawform_app.content_law_input.data = contract.content
        contractlawform_app.amount_law_input.data = contract.amount
        contractlawform_app.applier_law_input.data = label_dict.all_users_dict[contract.applieruid]
        contractlawform_app.applytime_law_input.data = contract.applytime
        if contract.crossuid is None:
            contractlawform_app.cvuser_law_input.data = ""
        else:
            contractlawform_app.cvuser_law_input.data = label_dict.all_users_dict[contract.crossuid]
        if contract.procedure|0b1111111110 == 0b1111111111:
            contractlawform_app.cvcontent_law_input.data = "[系统提示]具有前置流程的申请无需交叉复核。前置流程完整性暂须财务复核确认。"
        elif contract.procedure|0b1111111100 == 0b1111111111:
            contractlawform_app.cvcontent_law_input.data = "[系统提示]具有前置流程的申请无需交叉复核。前置流程完整性已经财务复核确认。"
        else:
            contractlawform_app.cvcontent_law_input.data = contract.crosscontent
        if contract.crossopinion is None:
            contractlawform_app.cvopinion_law_input.data = ""
        else:
            contractlawform_app.cvopinion_law_input.data = {True:"有异议",False:"无异议"}[contract.crossopinion]
        contractlawform_app.cvtime_law_input.data = contract.crosstime
        if contract.accuid is None:
            contractlawform_app.acc_law_input.data = ""
        else:
            contractlawform_app.acc_law_input.data = label_dict.all_users_dict[contract.accuid]
        contractlawform_app.acccontent_law_input.data = contract.acccontent
        if contract.accopinion is None:
            contractlawform_app.accopinion_law_input.data = ""
        else:
            contractlawform_app.accopinion_law_input.data = {True:"有异议",False:"无异议"}[contract.accopinion]
        contractlawform_app.acctime_law_input.data = contract.acctime

    else:
        return render_template('404.html'), 404


    if contractlawform_app.validate_on_submit():
        if contract.procedure|0b1111101111 == 0b1111111111:
            flash("本合同已经过法务复核，请不要重复提交。")
            return redirect(url_for('work.addrules'))

        if contractlawform_app.lawopinion_law_input.data == "0":
            contract.lawyeropinion = False
        elif contractlawform_app.lawopinion_law_input.data == "1":
            contract.lawyeropinion = True

        contract.procedure = contract.procedure|0b10000
        contract.lawyeruid = current_user.uid
        contract.lawyercontent = contractlawform_app.lawcontent_law_input.data
        contract.lawyertime = datetime.now(tz)
        mydb.session.add(contract)# pylint: disable=no-member
        mydb.session.commit()# pylint: disable=no-member

        return redirect(url_for('work.contractreview'))

    return render_template('work/contractonlaw.html', contractlawform_disp=contractlawform_app,
                           contract=contract, label_dict=label_dict)



@work.route('/contractonacc/<contractid>', methods=['GET', 'POST'])
@login_required
def contractonacc(contractid):
    """财务复核页面"""

    #调整时区
    pytz.country_timezones('cn')
    tz = pytz.timezone('Asia/Shanghai')
    label_dict = LabelDict()

    contract = Contracts.query.filter_by(idcontracts=contractid).first()
    if contract is not None:

        operation = Operations.query.filter_by(opcode=contract.opcode).first()# pylint: disable=C0301

        #如果第六位是1的话，表示已经财务复核完毕。
        if contract.procedure|0b1111011111 == 0b1111111111:
            flash("本合同已经过财务复核。")
            return redirect(url_for('work.addrules'))

        #判断当前用户是否无部门长、董事长权限，且有权限进行财务复核，且不等于applier
        #对应部门长及董事长
        inchargetest = Permissions.query.filter(or_(\
            and_(Permissions.puid == current_user.uid, \
            Permissions.companyid == contract.companyid, \
            Permissions.positionid == 2, Permissions.termstart <= datetime.now(tz), \
            Permissions.termend >= datetime.now(tz), Permissions.valid == True),\
            and_(Permissions.puid == current_user.uid, \
            Permissions.companyid == contract.companyid, \
            Permissions.positionid == contract.applydpt, Permissions.termstart <= datetime.now(tz),\
            Permissions.termend >= datetime.now(tz), Permissions.valid == True))).first()
        #法务复核人
        acctest = Lawyers.query.filter(and_(Lawyers.companyid == contract.companyid,\
            Lawyers.consultant == 2, \
            Lawyers.consultantuid == current_user.uid)).first()
        if acctest is None:
            flash("您无财务复核权限。")
            return redirect(url_for('work.addrules'))
        elif (inchargetest is not None) or (contract.applieruid == current_user.uid):
            flash("您有与财务复核不相容的权限或角色。")
            return redirect(url_for('work.addrules'))


        #填充表单数据
        contractaccform_app = ContractAccForm()
        contractaccform_app.company_acc_input.data = label_dict.all_company_dict[contract.companyid]
        contractaccform_app.applydpt_acc_input.data = label_dict.all_dpt_dict[contract.applydpt]
        contractaccform_app.contracttype_acc_input.data = operation.opname
        contractaccform_app.content_acc_input.data = contract.content
        contractaccform_app.amount_acc_input.data = contract.amount
        contractaccform_app.applier_acc_input.data = label_dict.all_users_dict[contract.applieruid]
        contractaccform_app.applytime_acc_input.data = contract.applytime

        if contract.crossuid is None:
            contractaccform_app.cvuser_acc_input.data = ""
        else:
            contractaccform_app.cvuser_acc_input.data = label_dict.all_users_dict[contract.crossuid]
        if contract.procedure|0b1111111110 == 0b1111111111:
            contractaccform_app.cvcontent_acc_input.data = "[系统提示]具有前置流程的申请无需交叉复核。前置流程完整性暂须财务复核确认。"
        elif contract.procedure|0b1111111100 == 0b1111111111:
            contractaccform_app.cvcontent_acc_input.data = "[系统提示]具有前置流程的申请无需交叉复核。前置流程完整性已经财务复核确认。"
        else:
            contractaccform_app.cvcontent_acc_input.data = contract.crosscontent
        if contract.crossopinion is None:
            contractaccform_app.cvopinion_acc_input.data = ""
        else:
            contractaccform_app.cvopinion_acc_input.data = {True:"有异议",False:"无异议"}[contract.crossopinion]
        contractaccform_app.cvtime_acc_input.data = contract.crosstime
        #lawyer
        if contract.lawyeruid is None:
            contractaccform_app.lawyer_acc_input.data = ""
        else:
            contractaccform_app.lawyer_acc_input.data = label_dict.all_users_dict[contract.lawyeruid]
        contractaccform_app.lawcontent_acc_input.data = contract.lawyercontent
        if contract.lawyeropinion is None:
            contractaccform_app.lawopinion_acc_input.data = ""
        else:
            contractaccform_app.lawopinion_acc_input.data = {True:"有异议",False:"无异议"}[contract.lawyeropinion]
        contractaccform_app.lawyertime_acc_input.data = contract.lawyertime


    else:
        return render_template('404.html'), 404


    if contractaccform_app.validate_on_submit():
        if contract.procedure|0b1111011111 == 0b1111111111:
            flash("本合同已经过财务复核，请不要重复提交。")
            return redirect(url_for('work.addrules'))

        if contractaccform_app.accopinion_acc_input.data == "0":
            contract.accopinion = False
        elif contractaccform_app.accopinion_acc_input.data == "1":
            contract.accopinion = True

        contract.procedure = contract.procedure|0b100010 #目前暂时把前置流程也交给财务复核通过，第二位变1
        contract.accuid = current_user.uid
        contract.acccontent = contractaccform_app.acccontent_acc_input.data
        contract.acctime = datetime.now(tz)
        mydb.session.add(contract)# pylint: disable=no-member
        mydb.session.commit()# pylint: disable=no-member

        return redirect(url_for('work.contractreview'))

    return render_template('work/contractonacc.html', contractaccform_disp=contractaccform_app,
                           contract=contract, label_dict=label_dict)




@work.route('/contractondpt/<contractid>', methods=['GET', 'POST'])
@login_required
def contractondpt(contractid):
    """部门长一级复核页面"""

    #调整时区
    pytz.country_timezones('cn')
    tz = pytz.timezone('Asia/Shanghai')
    label_dict = LabelDict()

    contract = Contracts.query.filter_by(idcontracts=contractid).first()

    operation = Operations.query.filter_by(opcode=contract.opcode).first()# pylint: disable=C0301
    
    contractdptform_app = ContractDPTForm()

    #判断是否具有本部门部门长授权范围内的权限，或者董事长权限
    ispresident = Permissions.query.filter(and_(Permissions.companyid==contract.companyid,
                                           Permissions.termstart <= datetime.now(tz),
                                           Permissions.termend >= datetime.now(tz),
                                           Permissions.valid == True,
                                           Permissions.puid==current_user.uid)).first()

    isincharge = Permissions.query.filter(and_(Permissions.companyid==contract.companyid,
                                           Permissions.positionid==contract.applydpt,
                                           Permissions.termstart <= datetime.now(tz),
                                           Permissions.termend >= datetime.now(tz),
                                           Permissions.valid == True,
                                           Permissions.puid == current_user.uid,
                                           eval("Permissions."+operation.opapprvcode+">=contract.amount"))).first()

    dptpermission = Permissions.query.filter(and_(Permissions.companyid==contract.companyid,
                                           Permissions.positionid==contract.applydpt,
                                           Permissions.termstart <= datetime.now(tz),
                                           Permissions.termend >= datetime.now(tz),
                                           Permissions.valid == True,
                                           eval("Permissions."+operation.opapprvcode+">=contract.amount"))).first()


    if contract is not None:
        #如果第七位是1的话，表示部门长已经审批过。
        if contract.procedure|0b1110111111 == 0b1111111111:
            flash("本合同已经部门负责人审批。")
            return redirect(url_for('work.addrules'))
        #如果三复核都通过了才能进行批复，否则跳出。
        if not (contract.procedure&0b0000110011 == 0b0000110011 or
            contract.procedure&0b0000111100 == 0b0000111100):
            flash("本合同尚未流转到批准阶段。")
            return redirect(url_for('work.addrules'))

        #还要判断部门长是否处于不相容职能中
        if current_user.uid in [contract.applieruid, contract.crossuid, contract.lawyeruid, contract.accuid]:
            flash("您有与批准订立合同不相容的权限或角色。")
            return redirect(url_for('work.addrules'))


        if dptpermission is not None:#有可操作的部门长前提下
            if ispresident is not None and isincharge is None:#本用户只有董事长权限
                flash("本合同应由部门长批准。")
                return redirect(url_for('work.addrules'))
            elif ispresident is None and isincharge is None:#本用户无董事长权限也无部门长权限
                flash("您无批准本合同的相应权限。")
                return redirect(url_for('work.addrules'))
        elif ispresident is None:#本用户无董事长权限
            flash("本合同应由董事长批准。")
            return redirect(url_for('work.addrules'))

        #准备填充数据
        contractdptform_app.company_dpt_input.data = label_dict.all_company_dict[contract.companyid]
        contractdptform_app.applydpt_dpt_input.data = label_dict.all_dpt_dict[contract.applydpt]
        contractdptform_app.contracttype_dpt_input.data = operation.opname
        contractdptform_app.content_dpt_input.data = contract.content
        contractdptform_app.amount_dpt_input.data = contract.amount
        contractdptform_app.applier_dpt_input.data = label_dict.all_users_dict[contract.applieruid]
        contractdptform_app.applytime_dpt_input.data = contract.applytime

        if contract.crossuid is None:
            contractdptform_app.cvuser_dpt_input.data = ""
        else:
            contractdptform_app.cvuser_dpt_input.data = label_dict.all_users_dict[contract.crossuid]
        if contract.procedure|0b1111111110 == 0b1111111111:
            contractdptform_app.cvcontent_dpt_input.data = "[系统提示]具有前置流程的申请无需交叉复核。前置流程完整性暂须财务复核确认。"
        elif contract.procedure|0b1111111100 == 0b1111111111:
            contractdptform_app.cvcontent_dpt_input.data = "[系统提示]具有前置流程的申请无需交叉复核。前置流程完整性已经财务复核确认。"
        else:
            contractdptform_app.cvcontent_dpt_input.data = contract.crosscontent
        if contract.crossopinion is None:
            contractdptform_app.cvopinion_dpt_input.data = ""
        else:
            contractdptform_app.cvopinion_dpt_input.data = {True:"有异议",False:"无异议"}[contract.crossopinion]
        contractdptform_app.cvtime_dpt_input.data = contract.crosstime
        #lawyer
        if contract.lawyeruid is None:
            contractdptform_app.lawyer_dpt_input.data = ""
        else:
            contractdptform_app.lawyer_dpt_input.data = label_dict.all_users_dict[contract.lawyeruid]
        contractdptform_app.lawcontent_dpt_input.data = contract.lawyercontent
        if contract.lawyeropinion is None:
            contractdptform_app.lawopinion_dpt_input.data = ""
        else:
            contractdptform_app.lawopinion_dpt_input.data = {True:"有异议",False:"无异议"}[contract.lawyeropinion]
        contractdptform_app.lawyertime_dpt_input.data = contract.lawyertime
        #acc
        if contract.accuid is None:
            contractdptform_app.acc_dpt_input.data = ""
        else:
            contractdptform_app.acc_dpt_input.data = label_dict.all_users_dict[contract.accuid]
        contractdptform_app.acccontent_dpt_input.data = contract.acccontent
        if contract.accopinion is None:
            contractdptform_app.accopinion_dpt_input.data = ""
        else:
            contractdptform_app.accopinion_dpt_input.data = {True:"有异议",False:"无异议"}[contract.accopinion]
        contractdptform_app.acctime_dpt_input.data = contract.acctime


    else:
        return render_template('404.html'), 404



    if contractdptform_app.validate_on_submit():
        if contract.procedure|0b1110111111 == 0b1111111111:
            flash("本合同已经部门负责人审批。")
            return redirect(url_for('work.addrules'))

        #如果三复核都通过了才能进行批复，否则跳出。
        if not (contract.procedure&0b0000110011 == 0b0000110011 or
            contract.procedure&0b0000111100 == 0b0000111100):
            flash("本合同尚未流转到批准阶段。")
            return redirect(url_for('work.addrules'))

        #还要判断部门长是否处于不相容职能中
        if current_user.uid in [contract.applieruid, contract.crossuid, contract.lawyeruid, contract.accuid]:
            flash("您有与批准订立合同不相容的权限或角色。")
            return redirect(url_for('work.addrules'))

        if dptpermission is not None:#有可操作的部门长前提下
            if ispresident is not None and isincharge is None:#本用户只有董事长权限
                flash("本合同应由部门长批准。")
                return redirect(url_for('work.addrules'))
            elif ispresident is None and isincharge is None:#本用户无董事长权限也无部门长权限
                flash("您无批准本合同的相应权限。")
                return redirect(url_for('work.addrules'))
        elif ispresident is None:#本用户无董事长权限
            flash("本合同应由董事长批准。")
            return redirect(url_for('work.addrules'))


        contract.procedure = contract.procedure|0b1000000 #第七位变1
        #这里要预留一个激发二级审批的开关
        if dptpermission is None and ispresident is not None:
            contract.authid = ispresident.idpermission
        elif isincharge is not None:
            contract.authid = isincharge.idpermission
        contract.approveruid = current_user.uid
        if contractdptform_app.apprvopinion_dpt_input.data == "0":
            contract.apprvopinion = False
        elif contractdptform_app.apprvopinion_dpt_input.data == "1":
            contract.apprvopinion = True
        contract.apprvtime = datetime.now(tz)

        mydb.session.add(contract)# pylint: disable=no-member
        mydb.session.commit()# pylint: disable=no-member

        return redirect(url_for('work.contractreview'))



    return render_template('work/contractondpt.html', contractdptform_disp=contractdptform_app,
                           contract=contract, label_dict=label_dict)





@work.route('/contractreview')
@login_required
def contractreview():
    """待审批合同列表"""

    #调整时区
    pytz.country_timezones('cn')
    tz = pytz.timezone('Asia/Shanghai')

    dptreview = []#None
    cvreview = []#None
    lawreview = []#None
    accreview = []#None

    # 鉴定同公司董事长权限
    president = Permissions.query.filter(Permissions.positionid==2, Permissions.puid==current_user.uid, \
        Permissions.termstart <= datetime.now(tz), Permissions.termend >= datetime.now(tz), \
        Permissions.valid == True).all()
    president_list = [pd.companyid for pd in president]
    # 鉴定同公司同部门长权限
    inchargedpt = Permissions.query.filter(Permissions.puid==current_user.uid, \
        Permissions.termstart <= datetime.now(tz), Permissions.termend >= datetime.now(tz), \
        Permissions.valid == True).all()
    incharge_list = [[incharge.companyid, incharge.positionid] for incharge in inchargedpt]
    # 鉴定cv部门权限
    crossvalid = Crossvalids.query.filter(Crossvalids.crossuid==current_user.uid).all()
    cv_list = [[cv.companyid, cv.crossdpt] for cv in crossvalid]
    # 鉴定law权限
    lawyer = Lawyers.query.filter(and_(Lawyers.consultantuid==current_user.uid, Lawyers.consultant==1)).all()
    lawyer_list = [law.companyid for law in lawyer]
    # 鉴定acc权限
    accountant = Lawyers.query.filter(and_(Lawyers.consultantuid==current_user.uid, Lawyers.consultant==2)).all()
    acc_list = [acc.companyid for acc in accountant]


    allcontract = Contracts.query.order_by(Contracts.applytime.desc()).all()

    #可见一级审批表
    for contract in allcontract:
        if ((contract.procedure&0b0000110011 == 0b0000110011 or contract.procedure&0b0000111100 == 0b0000111100) and #需要审批
            contract.procedure|0b1110111111==0b1110111111 and #尚未审批
            contract.applieruid!=current_user.uid and #当前用户不是申请人
            contract.crossuid!=current_user.uid and #当前用户不是交叉复核人
            contract.lawyeruid!=current_user.uid and #当前用户不是法务
            contract.accuid!=current_user.uid and #当前用户不是财务
            (([contract.companyid, contract.applydpt] in incharge_list) or contract.companyid in president_list)): 
            dptreview.append(contract)


    #可见cv表
    for contract in allcontract:
        if (contract.procedure|0b1111111011==0b1111111111 and #需要cv
            contract.procedure|0b1111110111==0b1111110111 and #尚未cv
            contract.applieruid!=current_user.uid and #当前用户不是申请人
            ([contract.companyid, contract.applydpt] in cv_list) and #有cv权限
            contract.companyid not in president_list and #无董事长权限
            ([contract.companyid, contract.applydpt] not in incharge_list)): #无部门长权限
            cvreview.append(contract)

    #可见law表
    for contract in allcontract:
        if (contract.procedure|0b1111101111==0b1111101111 and #尚未law
            contract.applieruid!=current_user.uid and #当前用户不是申请人
            (contract.companyid in lawyer_list) and #有lawyer权限
            (contract.companyid not in president_list) and #无董事长权限
            ([contract.companyid, contract.applydpt] not in incharge_list)): #无部门长权限
            lawreview.append(contract)

    #可见acc表
    for contract in allcontract:
        if (contract.procedure|0b1111011111==0b1111011111 and #尚未acc
            contract.applieruid!=current_user.uid and #当前用户不是申请人
            (contract.companyid in acc_list) and #有acc权限
            (contract.companyid not in president_list) and #无董事长权限
            ([contract.companyid, contract.applydpt] not in incharge_list)): #无部门长权限
            accreview.append(contract)



    label_dict = LabelDict()

    return render_template('work/contractreview.html', dptreview=dptreview,
                           cvreview=cvreview, lawreview=lawreview, accreview=accreview,
                           label_dict=label_dict)


@work.route('/contractrules')
@login_required
def contractrules():
    """合同申请流程说明"""

    return render_template('work/contractrules.html')
