"""
learn flask work
"""
# pylint: disable=invalid-name

from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField, PasswordField, BooleanField, ValidationError # pylint: disable=C0301
from wtforms.validators import Required, Length, Regexp
from ..models import Payments, Approvers

class PayapplyForm(FlaskForm):
    """payment aplly form class"""
    dpt_apply_input = SelectField('使用部门', validators=[Required()])
    budgettype_apply_input = SelectField('费用类型', validators=[Required()], choices = [("", "---"), ("采购","采购"),("工程","工程"),("报销","报销"),("费用","费用")]) # pylint: disable=C0301
    content_apply_input = StringField('申请内容', validators=[Required(), Length(1, 64)]) 
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
