"""
learn flask work
"""
# pylint: disable=invalid-name

from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, TextAreaField, SubmitField, PasswordField, BooleanField, ValidationError # pylint: disable=C0301
from wtforms.fields.html5 import DateField
from wtforms.validators import Required, Length, Regexp
from ..models import Payments, Approvers, Permissions, User, Departments, Operations
from flask_login import current_user
from sqlalchemy import and_



class LabelDict():
    """常用数据类，等到视图函数内再实例化"""
    def __init__(self, *args, **kwargs):
        self.all_users_dict = {} #用户id姓名字典
        all_users = User.query.all()
        for user in all_users:
            self.all_users_dict[user.uid] = user.name

        self.all_dpt_dict = {} #部门id名称字典
        self.all_dptincharge_dict = {} #部门长名称字典
        all_dpt = Departments.query.all()
        for dpt in all_dpt:
            self.all_dpt_dict[dpt.iddepartments] = dpt.dptname
            self.all_dptincharge_dict[dpt.iddepartments] = dpt.dptincharge

        self.all_company_dict = {1:'辉文',2:'植森',3:'蓓蒂森'} #公司名称字典



class PayapplyForm(FlaskForm):
    """payment apply form class"""
    dpt_apply_input = SelectField('使用部门', validators=[Required()])
    budgettype_apply_input = SelectField('费用类型', validators=[Required()], choices = [("", "---"), ("采购","采购"),("工程","工程"),("报销","报销"),("费用","费用")]) # pylint: disable=C0301
    content_apply_input = TextAreaField('申请内容', validators=[Required(), Length(1, 1024)]) 
    amount_apply_input = StringField('申请金额', validators=[Required(), Length(1, 20), Regexp('^[0-9]+(.[0-9]{2})?$', 0, '使用金额格式，例：1234.56')])  # pylint: disable=C0301
    approveruid_apply_input =  StringField('审批人', render_kw={'readonly': True})
    submit_pay_btn = SubmitField('提交')

    def __init__(self, **kwargs):
        """从approvers表内载入部门选项"""
        super(PayapplyForm, self).__init__(**kwargs)
        dpt_all = [("", "---")]
        for dpt in Approvers.query.all():
            dpt_all.append((str(dpt.idapprover),dpt.dpt))
        self.dpt_apply_input.choices = dpt_all


class Paydetail(FlaskForm):
    """Payment detail for approver"""
    applier_view =  StringField('申请人', render_kw={'readonly': True})
    applytime_view = StringField('申请时间', render_kw={'readonly': True})
    dpt_view = StringField('使用部门', render_kw={'readonly': True})
    budgettype_view = StringField('费用类型', render_kw={'readonly': True})
    amount_view = StringField('申请金额', render_kw={'readonly': True})
    content_view = TextAreaField('申请内容', render_kw={'readonly': True})
    opinion = SelectField('审批意见', validators=[Required()], choices = [("", "---"), ("1","同意"),("0","拒绝")]) # pylint: disable=C0301
    submit_view_btn = SubmitField('提交审批')


class AddPermissionForm(FlaskForm):
    """add new permission form class"""

    company_addpm_input = SelectField('授权公司范围', validators=[Required()])
    position_addpm_input = SelectField('授予职能', validators=[Required()])
    usercompany_addpm_input = SelectField('被授权人所属公司', validators=[Required()])
    userdpt_addpm_input = SelectField('被授权人所在部门', validators=[Required()])
    user_addpm_input = SelectField('被授权人员', validators=[Required()], choices = [("", "---")])
    term_addpm_input = SelectField('长期/临时',validators=[Required()], choices=[('2','临时'),('1','长期')])
    termstart_addpm_input = DateField('授权开始日期', validators=[Required()], format='%Y-%m-%d')
    termend_addpm_input = DateField('授权结束日期', validators=[Required()], format='%Y-%m-%d')
    apprv100001_addpm_input = StringField('1. 批准销售框架合同金额', default='0.00', validators=[Required(), Length(1, 20), Regexp('^[0-9]+(.[0-9]{2})?$', 0, '使用金额格式，例：1234.56')])  # pylint: disable=C0301
    apprv100002_addpm_input = StringField('2. 批准销售订单合同金额', default='0.00', validators=[Required(), Length(1, 20), Regexp('^[0-9]+(.[0-9]{2})?$', 0, '使用金额格式，例：1234.56')])  # pylint: disable=C0301
    apprv100003_addpm_input = StringField('3. 批准提供服务合同金额', default='0.00', validators=[Required(), Length(1, 20), Regexp('^[0-9]+(.[0-9]{2})?$', 0, '使用金额格式，例：1234.56')])  # pylint: disable=C0301
    apprv100004_addpm_input = StringField('4. 批准原辅料采购框架合同金额', default='0.00', validators=[Required(), Length(1, 20), Regexp('^[0-9]+(.[0-9]{2})?$', 0, '使用金额格式，例：1234.56')])  # pylint: disable=C0301
    apprv100005_addpm_input = StringField('5. 批准原辅料采购订单合同金额', default='0.00', validators=[Required(), Length(1, 20), Regexp('^[0-9]+(.[0-9]{2})?$', 0, '使用金额格式，例：1234.56')])  # pylint: disable=C0301
    apprv100006_addpm_input = StringField('6. 批准产品外包加工合同金额', default='0.00', validators=[Required(), Length(1, 20), Regexp('^[0-9]+(.[0-9]{2})?$', 0, '使用金额格式，例：1234.56')])  # pylint: disable=C0301
    apprv100007_addpm_input = StringField('7. 批准工程合同金额', default='0.00', validators=[Required(), Length(1, 20), Regexp('^[0-9]+(.[0-9]{2})?$', 0, '使用金额格式，例：1234.56')])  # pylint: disable=C0301
    apprv100008_addpm_input = StringField('8. 批准固定资产采购合同金额', default='0.00', validators=[Required(), Length(1, 20), Regexp('^[0-9]+(.[0-9]{2})?$', 0, '使用金额格式，例：1234.56')])  # pylint: disable=C0301
    apprv100009_addpm_input = StringField('9. 批准专利无形资产采购合同金额', default='0.00', validators=[Required(), Length(1, 20), Regexp('^[0-9]+(.[0-9]{2})?$', 0, '使用金额格式，例：1234.56')])  # pylint: disable=C0301
    apprv100010_addpm_input = StringField('10. 批准外包服务合同金额', default='0.00', validators=[Required(), Length(1, 20), Regexp('^[0-9]+(.[0-9]{2})?$', 0, '使用金额格式，例：1234.56')])  # pylint: disable=C0301
    apprv100011_addpm_input = StringField('11. 批准借款合同金额', default='0.00', validators=[Required(), Length(1, 20), Regexp('^[0-9]+(.[0-9]{2})?$', 0, '使用金额格式，例：1234.56')])  # pylint: disable=C0301
    apprv100012_addpm_input = StringField('12. 批准提供担保合同金额', default='0.00', validators=[Required(), Length(1, 20), Regexp('^[0-9]+(.[0-9]{2})?$', 0, '使用金额格式，例：1234.56')])  # pylint: disable=C0301
    apprv100013_addpm_input = StringField('13. 批准融资合同金额', default='0.00', validators=[Required(), Length(1, 20), Regexp('^[0-9]+(.[0-9]{2})?$', 0, '使用金额格式，例：1234.56')])  # pylint: disable=C0301
    apprv100014_addpm_input = StringField('14. 批准接收担保合同金额', default='0.00', validators=[Required(), Length(1, 20), Regexp('^[0-9]+(.[0-9]{2})?$', 0, '使用金额格式，例：1234.56')])  # pylint: disable=C0301
    apprv100015_addpm_input = StringField('15. 批准投资合同金额', default='0.00', validators=[Required(), Length(1, 20), Regexp('^[0-9]+(.[0-9]{2})?$', 0, '使用金额格式，例：1234.56')])  # pylint: disable=C0301
    apprv100016_addpm_input = StringField('16. 批准出售资产合同金额', default='0.00', validators=[Required(), Length(1, 20), Regexp('^[0-9]+(.[0-9]{2})?$', 0, '使用金额格式，例：1234.56')])  # pylint: disable=C0301
    apprv100017_addpm_input = StringField('17. 批准专利转让或许可合同金额', default='0.00', validators=[Required(), Length(1, 20), Regexp('^[0-9]+(.[0-9]{2})?$', 0, '使用金额格式，例：1234.56')])  # pylint: disable=C0301
    submit_addpm_btn = SubmitField('提交')

    def __init__(self, *args, **kwargs):
        """动态下拉选项，及预载入option防止pre_valid报错"""
        super(AddPermissionForm, self).__init__(*args, **kwargs)
        allusersoption = [("", "---")]
        for user in User.query.all():
            allusersoption.append((str(user.uid),user.name))
        self.user_addpm_input.choices = allusersoption

        label_dict = LabelDict()
        
        company_choices = [("", "---")]
        for key, value in label_dict.all_company_dict.items():
            company_choices.append((str(key), value))
        self.company_addpm_input.choices = company_choices
        self.usercompany_addpm_input.choices = company_choices

        dpt_choices = [("", "---")]
        for key, value in label_dict.all_dpt_dict.items():
            dpt_choices.append((str(key), value))
        self.userdpt_addpm_input.choices = dpt_choices

        position_choices = [("", "---")]
        positiondict_disp = dict((key, value) for key, value in label_dict.all_dptincharge_dict.items() if key ==2 or key>3) 
        for key, value in positiondict_disp.items():
            position_choices.append((str(key),value))
        self.position_addpm_input.choices = position_choices




class Permissiondetail(FlaskForm):
    """授权单详情"""
    idpermission_pmdt_input = StringField('授权书', render_kw={'readonly': True})
    company_pmdt_input = StringField('授权范围', render_kw={'readonly': True})
    position_pmdt_input = StringField('授予职能', render_kw={'readonly': True})
    usercompany_pmdt_input = StringField('被授权人所属公司', render_kw={'readonly': True})
    userdpt_pmdt_input = StringField('被授权人所在部门', render_kw={'readonly': True})
    user_pmdt_input = StringField('被授权人员', render_kw={'readonly': True})
    term_pmdt_input = StringField('长期/临时', render_kw={'readonly': True})
    termstart_pmdt_input = DateField('授权开始日期',format='%Y-%m-%d' ,render_kw={'readonly': True})
    termend_pmdt_input = DateField('授权结束日期', format='%Y-%m-%d', render_kw={'readonly': True})
    originstart_pmdt_input = DateField('原授权开始日期',format='%Y-%m-%d' ,render_kw={'readonly': True})
    originend_pmdt_input = DateField('原授权结束日期', format='%Y-%m-%d', render_kw={'readonly': True})
    valid_pmdt_input = StringField('当前是否生效', render_kw={'readonly': True})
    apprv100001_pmdt_input = StringField('1. 批准销售框架合同金额', render_kw={'readonly': True})
    apprv100002_pmdt_input = StringField('2. 批准销售订单合同金额', render_kw={'readonly': True})
    apprv100003_pmdt_input = StringField('3. 批准提供服务合同金额', render_kw={'readonly': True})
    apprv100004_pmdt_input = StringField('4. 批准原辅料采购框架合同金额', render_kw={'readonly': True})
    apprv100005_pmdt_input = StringField('5. 批准原辅料采购订单合同金额', render_kw={'readonly': True})
    apprv100006_pmdt_input = StringField('6. 批准产品外包加工合同金额', render_kw={'readonly': True})
    apprv100007_pmdt_input = StringField('7. 批准工程合同金额', render_kw={'readonly': True})
    apprv100008_pmdt_input = StringField('8. 批准固定资产采购合同金额', render_kw={'readonly': True})
    apprv100009_pmdt_input = StringField('9. 批准专利无形资产采购合同金额', render_kw={'readonly': True})
    apprv100010_pmdt_input = StringField('10. 批准外包服务合同金额', render_kw={'readonly': True})
    apprv100011_pmdt_input = StringField('11. 批准借款合同金额', render_kw={'readonly': True})
    apprv100012_pmdt_input = StringField('12. 批准提供担保合同金额', render_kw={'readonly': True})
    apprv100013_pmdt_input = StringField('13. 批准融资合同金额', render_kw={'readonly': True})
    apprv100014_pmdt_input = StringField('14. 批准接收担保合同金额', render_kw={'readonly': True})
    apprv100015_pmdt_input = StringField('15. 批准投资合同金额', render_kw={'readonly': True})
    apprv100016_pmdt_input = StringField('16. 批准出售资产合同金额', render_kw={'readonly': True})
    apprv100017_pmdt_input = StringField('17. 批准专利转让或许可合同金额', render_kw={'readonly': True})



class ContractApplyForm(FlaskForm):
    """提交合同审批单"""
    company_apply_input = SelectField('订立合同公司', validators=[Required()])
    applydpt_apply_input = SelectField('订立合同部门', validators=[Required()])
    contracttype_apply_input = SelectField('合同业务类型', validators=[Required()])
    content_apply_input = TextAreaField('合同内容', validators=[Required(), Length(1, 5120)]) 
    amount_apply_input = StringField('标的金额', validators=[Required(), Length(1, 20), Regexp('^[0-9]+(.[0-9]{2})?$', 0, '使用金额格式，例：1234.56')])  # pylint: disable=C0301
    submit_apply_btn = SubmitField('提交')

    def __init__(self, *args, **kwargs):
        """动态下拉选项"""
        super(ContractApplyForm, self).__init__(*args, **kwargs)
        
        label_dict = LabelDict()

        company_choices = [("", "---")]
        for key, value in label_dict.all_company_dict.items():
            company_choices.append((str(key), value))
        self.company_apply_input.choices = company_choices
        
        applydpt_choices = [("", "---")]
        applydptdict_disp = dict((key, value) for key, value in label_dict.all_dpt_dict.items() if key>3) 
        for key, value in applydptdict_disp.items():
            applydpt_choices.append((str(key),value))
        self.applydpt_apply_input.choices = applydpt_choices

        op_choices = [("", "---")]
        contractop = Operations.query.all()
        for op in contractop:
            if op.idoperations < 18:
                op_choices.append((str(op.idoperations),op.opname))
        self.contracttype_apply_input.choices = op_choices
