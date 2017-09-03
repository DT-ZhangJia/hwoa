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



class Permission:
    """Permissions"""
    FOLLOW = 0x01
    COMMENT = 0x02
    WRITE_ARTICLES = 0x04
    MODERATE_COMMENTS = 0x08
    ADMINISTER = 0x80

class Payments(mydb.Model):
    """Payments"""
    __tablename__ = 'payments'
    idpayment = mydb.Column(mydb.Integer, primary_key=True)
    applieruid = mydb.Column(mydb.Integer, mydb.ForeignKey('users.uid'))
    applytime = mydb.Column(mydb.DateTime)
    dpt = mydb.Column(mydb.String(64))
    budgettype = mydb.Column(mydb.String(64))
    content = mydb.Column(mydb.Text)
    amount = mydb.Column(mydb.Float)
    approveruid = mydb.Column(mydb.Integer, mydb.ForeignKey('users.uid'))
    opinion = mydb.Column(mydb.Boolean)

    def __repr__(self):
        return '<Payment %r>' % self.name

class Approvers(mydb.Model):
    """Approvers"""
    __tablename__ = 'approvers'
    idapprover = mydb.Column(mydb.Integer, primary_key=True)
    dpt = mydb.Column(mydb.String(64))
    approveruid = mydb.Column(mydb.Integer)

    def __repr__(self):
        return '<Approver %r>' % self.name

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
    dpt = mydb.Column(mydb.String(64))
    title = mydb.Column(mydb.String(64))
    confirmed = mydb.Column(mydb.Boolean, default=True)#临时全激活注册用户

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.role is None:
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
