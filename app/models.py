"""
learn flask models
"""
# pylint: disable=invalid-name, too-few-public-methods, no-member
# no-member是为了避免flask_sqlalchemy无法读取尚未执行的程序中的类而报错


from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app
from flask_login import UserMixin
from . import mydb, login_manager


class Departments(mydb.Model):
    """Departments"""
    __tablename__ = 'departments'
    iddepartments = mydb.Column(mydb.Integer, primary_key=True)
    dptname = mydb.Column(mydb.String(64))
    dptincharge = mydb.Column(mydb.String(64))

    def __repr__(self):
        return '<Department %r>' % self.iddepartments


class Payments(mydb.Model):
    """Payments"""
    __tablename__ = 'payments'
    idpayment = mydb.Column(mydb.Integer, primary_key=True)
    applieruid = mydb.Column(mydb.Integer, mydb.ForeignKey('users.uid'))
    applytime = mydb.Column(mydb.DateTime)
    dpt = mydb.Column(mydb.String(64))
    budgettype = mydb.Column(mydb.String(64))
    content = mydb.Column(mydb.String(1024))
    amount = mydb.Column(mydb.Float)
    approveruid = mydb.Column(mydb.Integer, mydb.ForeignKey('users.uid'))
    opinion = mydb.Column(mydb.Boolean)
    approvetime = mydb.Column(mydb.DateTime)

    def __repr__(self):
        return '<Payment %r>' % self.idpayment

class Approvers(mydb.Model):
    """Approvers"""
    __tablename__ = 'approvers'
    idapprover = mydb.Column(mydb.Integer, primary_key=True)
    dpt = mydb.Column(mydb.String(64))
    approveruid = mydb.Column(mydb.Integer)

    def __repr__(self):
        return '<Approver %r>' % self.idapprover


class Permissions(mydb.Model):
    """权限表"""
    __tablename__ = 'permissions'
    idpermission = mydb.Column(mydb.Integer, primary_key=True)
    companyid = mydb.Column(mydb.Integer)
    positionid = mydb.Column(mydb.Integer)
    puid = mydb.Column(mydb.Integer)
    term = mydb.Column(mydb.Integer)
    termstart = mydb.Column(mydb.DateTime)
    termend = mydb.Column(mydb.DateTime)
    originstart = mydb.Column(mydb.DateTime)
    originend = mydb.Column(mydb.DateTime)
    approved = mydb.Column(mydb.Boolean)
    valid = mydb.Column(mydb.Boolean)
    apprv100001 = mydb.Column(mydb.Float)
    apprv100002 = mydb.Column(mydb.Float)
    apprv100003 = mydb.Column(mydb.Float)
    apprv100004 = mydb.Column(mydb.Float)
    apprv100005 = mydb.Column(mydb.Float)
    apprv100006 = mydb.Column(mydb.Float)
    apprv100007 = mydb.Column(mydb.Float)
    apprv100008 = mydb.Column(mydb.Float)
    apprv100009 = mydb.Column(mydb.Float)
    apprv100010 = mydb.Column(mydb.Float)
    apprv100011 = mydb.Column(mydb.Float)
    apprv100012 = mydb.Column(mydb.Float)
    apprv100013 = mydb.Column(mydb.Float)
    apprv100014 = mydb.Column(mydb.Float)
    apprv100015 = mydb.Column(mydb.Float)
    apprv100016 = mydb.Column(mydb.Float)
    apprv100017 = mydb.Column(mydb.Float)
    apprv100018 = mydb.Column(mydb.Float)
    apprv100019 = mydb.Column(mydb.Float)


    def __repr__(self):
        return '<Permissions %r>' % self.idpermission


class Operations(mydb.Model):
    """业务类型"""
    __tablename__ = 'operations'
    idoperations = mydb.Column(mydb.Integer, primary_key=True)
    opcode = mydb.Column(mydb.String(32))
    opname = mydb.Column(mydb.String(64))
    opapprvcode = mydb.Column(mydb.String(32))
    opapprvname = mydb.Column(mydb.String(64))

    def __repr__(self):
        return '<Operations %r>' % self.idoperations



class Lawyers(mydb.Model):
    """法务财务复核"""
    __tablename__ = 'lawyers'
    idlawyer = mydb.Column(mydb.Integer, primary_key=True)
    companyid = mydb.Column(mydb.Integer)
    consultant = mydb.Column(mydb.Integer)
    consultantuid = mydb.Column(mydb.Integer)

    def __repr__(self):
        return '<Lawyers %r>' % self.idlawyer


class Crossvalids(mydb.Model):
    """交叉复核"""
    __tablename__ = 'crossvalids'
    idcrossvalids = mydb.Column(mydb.Integer, primary_key=True)
    companyid = mydb.Column(mydb.Integer)
    crossdpt = mydb.Column(mydb.Integer)
    crossuid = mydb.Column(mydb.Integer)

    def __repr__(self):
        return '<Crossvalids %r>' % self.idcrossvalids



class Contracts(mydb.Model):
    """合同审批流程"""
    __tablename__ = 'contracts'
    idcontracts = mydb.Column(mydb.Integer, primary_key=True)
    companyid = mydb.Column(mydb.Integer)
    applieruid = mydb.Column(mydb.Integer)
    applydpt = mydb.Column(mydb.Integer)
    applytime = mydb.Column(mydb.DateTime)
    opcode = mydb.Column(mydb.String(32))
    content = mydb.Column(mydb.String(5120))
    amount = mydb.Column(mydb.Float)
    procedure = mydb.Column(mydb.Integer) #这个字段是重点
    preprocess = mydb.Column(mydb.Boolean)
    crossdpt = mydb.Column(mydb.Integer)
    crossuid = mydb.Column(mydb.Integer)
    crossopinion = mydb.Column(mydb.Boolean) #假设True是无异议
    crosscontent = mydb.Column(mydb.String(2048))
    crosstime = mydb.Column(mydb.DateTime)
    lawyeruid = mydb.Column(mydb.Integer)
    lawyeropinion = mydb.Column(mydb.Boolean) #假设True是无异议
    lawyercontent = mydb.Column(mydb.String(2048))
    lawyertime = mydb.Column(mydb.DateTime)
    accuid = mydb.Column(mydb.Integer)
    accopinion = mydb.Column(mydb.Boolean) #假设True是无异议
    acccontent = mydb.Column(mydb.String(2048))
    acctime = mydb.Column(mydb.DateTime)
    authid = mydb.Column(mydb.Integer)
    approveruid = mydb.Column(mydb.Integer)
    apprvopinion = mydb.Column(mydb.Boolean)
    apprvtime = mydb.Column(mydb.DateTime)
    lv2approveruid = mydb.Column(mydb.Integer)
    lv2apprvopinion = mydb.Column(mydb.Boolean)
    lv2apprvtime = mydb.Column(mydb.DateTime)
    stamperuid = mydb.Column(mydb.Integer)
    stamptime = mydb.Column(mydb.DateTime)
    originalcontractid = mydb.Column(mydb.Integer)
    stopcontractid = mydb.Column(mydb.Integer)
    updatecontractid = mydb.Column(mydb.Integer)
    deleted = mydb.Column(mydb.Boolean)


    def __repr__(self):
        return '<Contracts %r>' % self.idcontracts



class Role(mydb.Model):
    """role"""
    __tablename__ = 'roles'
    uid = mydb.Column(mydb.Integer, primary_key=True)
    name = mydb.Column(mydb.String(64), unique=True)
    default = mydb.Column(mydb.Boolean, default=False, index=True)
    permissions = mydb.Column(mydb.Integer)
    user = mydb.relationship('User', backref='role', lazy='dynamic')

    def __repr__(self):
        return '<Role %r>' % self.name

class User(UserMixin, mydb.Model):
    """user"""
    __tablename__ = 'users'
    uid = mydb.Column(mydb.Integer, primary_key=True)
    #id = uid #如果不手动设置这个id的参数，则get_id方法就报错，奇怪！
    username = mydb.Column(mydb.String(64), unique=True, index=True)
    name = mydb.Column(mydb.String(64))
    email = mydb.Column(mydb.String(64), unique=True, index=True)
    passwd_hash = mydb.Column(mydb.String(128))
    role_id = mydb.Column(mydb.Integer, mydb.ForeignKey('roles.uid'))
    company = mydb.Column(mydb.Integer)
    dpt = mydb.Column(mydb.Integer)
    title = mydb.Column(mydb.String(64))
    confirmed = mydb.Column(mydb.Boolean, default=True)#临时全激活注册用户

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.role is None: # pylint: disable=E0203
            #if self.email == current_app.config['FLASKY_ADMIN']:
            #    self.role = Role.query.filter_by(permissions=0xff).first()
            #if self.role is None:
            self.role = Role.query.filter_by(default=True).first()

    @property
    def passwd(self):
        """设置无法读取密码属性"""
        raise AttributeError('无法读取')

    @passwd.setter
    def passwd(self, passwd):
        """生成密码离散值"""
        self.passwd_hash = generate_password_hash(passwd)

    def verify_passwd(self, passwd):
        """验证离散值密码"""
        return check_password_hash(self.passwd_hash, passwd)

    def get_id(self): #自己创建get_id方法，"override"覆盖usermixin里默认设置的返回self.id属性
        return self.uid #自设的user实例中的属性是uid

    def generate_confirmation_token(self, expiration=300):
        """生成注册确认令牌"""
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm': self.uid})

    def confirm(self, token):
        """验证存在"""
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except: # pylint: disable=W0702
            return False
        if data.get('confirm') != self.uid:#这个检测有什么意义？
            return False
        self.confirmed = True
        mydb.session.add(self)
        return True

    def generate_resetpw_token(self, expiration=3600):
        """生成重置密码确认令牌"""
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'reset': self.uid})

    def reset_password(self, token, new_password):
        """写入重置的新密码"""
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except: # pylint: disable=W0702
            return False
        if data.get('reset') != self.uid:#reset的时候需要核对邮箱与申请重置的是同一个用户
            return False
        #self.passwd = new_password
        self.passwd_hash = generate_password_hash(new_password)
        mydb.session.add(self)
        return True #放在这里难道是永恒为true？


    def __repr__(self):
        return '<User %r>' % self.username

@login_manager.user_loader
def load_user(user_id):
    """用户存在性回调函数"""
    return User.query.get(int(user_id)) #这个回调函数难以理解，参见pocket内记载



class Assets(mydb.Model):
    """固定资产记录"""
    __tablename__ = 'assets'
    idassets = mydb.Column(mydb.Integer, primary_key=True)
    syscode = mydb.Column(mydb.Integer)
    subcode = mydb.Column(mydb.Integer)
    assetname = mydb.Column(mydb.String(256))
    accountid = mydb.Column(mydb.Integer)
    classid = mydb.Column(mydb.Integer)
    companyid = mydb.Column(mydb.Integer)
    dptid = mydb.Column(mydb.Integer)
    originvalue = mydb.Column(mydb.Float)
    originmonth = mydb.Column(mydb.Integer)
    remainmonth = mydb.Column(mydb.Integer)
    netsalvage = mydb.Column(mydb.Float)
    monthdep = mydb.Column(mydb.Float)
    purchasedate = mydb.Column(mydb.Date)
    starttype = mydb.Column(mydb.Integer)
    termstart = mydb.Column(mydb.Date)
    startmemo = mydb.Column(mydb.String(256))
    endtype = mydb.Column(mydb.Integer)
    termend = mydb.Column(mydb.Date)
    endmemo = mydb.Column(mydb.String(256))
    withdep = mydb.Column(mydb.Float)
    syswithdep = mydb.Column(mydb.Float)
    isdep = mydb.Column(mydb.Boolean)
    originid = mydb.Column(mydb.Integer)
    placeid = mydb.Column(mydb.Integer)
    keeperuid = mydb.Column(mydb.Integer)
    model = mydb.Column(mydb.String(256))
    label = mydb.Column(mydb.String(256))
    origincode = mydb.Column(mydb.Integer)
    provider = mydb.Column(mydb.String(256))
    notes = mydb.Column(mydb.String(2048))


    def __repr__(self):
        return '<Assets %r>' % self.idassets
