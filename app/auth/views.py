"""
learn flask views
"""
# pylint: disable=invalid-name

from flask import render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, logout_user, login_required, current_user
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from . import auth
from ..models import User
from .forms import LoginForm, RegisterForm, ChangepwForm, ResetrequestForm, PasswordResetForm
from .. import mydb
from ..email import send_email


@auth.route('/login', methods=['GET', 'POST'])
def login():
    """login"""
    loginform_app = LoginForm()
    wrongpw = True #初始化密码错误状态开关值
    if loginform_app.validate_on_submit():
        userlogin_check = User.query.filter_by(email=loginform_app.email_input.data).first()
        wrongpw = userlogin_check.verify_passwd(loginform_app.passwd_input.data) #log时核对密码更新开关值
        if userlogin_check is not None and userlogin_check.verify_passwd(loginform_app.passwd_input.data):# pylint: disable=C0301
            login_user(userlogin_check, loginform_app.remember_me_box.data)
            #next参数不知道是哪里来的
            return redirect(request.args.get('next') or url_for('main.index'))
        flash('邮箱或密码错误。')
    return render_template('auth/login.html', loginform_display=loginform_app, wrongpw=wrongpw) #将密码错误开关传入页面 # pylint: disable=C0301

@auth.route('/logout')
@login_required #login_manager unauthorized 强制跳转到login_view
def logout():
    """logout"""
    logout_user()
    flash('您已登出系统。') #这个flash到main.index上去了
    return redirect(url_for('main.index'))

@auth.route('/register', methods=['GET', 'POST'])
def register():
    """register new user"""

    
    flash('目前未开放注册。') #这个flash到main.index上去了
    return redirect(url_for('main.index'))


    """
    registerform_app = RegisterForm()
    if registerform_app.validate_on_submit():
        newuser = User(email=registerform_app.email_reg_input.data,
                       username=registerform_app.username_reg_input.data,
                       passwd=registerform_app.passwd_reg_input.data)
        mydb.session.add(newuser)# pylint: disable=no-member
        mydb.session.commit()# pylint: disable=no-member 需要立刻提交数据库以获得id
        #临时取消邮件确认
        #token = newuser.generate_confirmation_token()
        #send_email(newuser.email, 'Confirm Your Account',
        #           'auth/email/confirm', mailuser=newuser, token=token)
        #flash('A confirmation email sent.')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', registerform_display=registerform_app)
    """    


@auth.route('/confirm/<token>')
@login_required
def confirmmail(token):
    """确认邮件url路由"""
    if current_user.confirmed:
        return redirect(url_for('main.index'))
    if current_user.confirm(token):
        flash('您已确认了您的帐号。谢谢！')
    else:
        flash('确认链接无效或者已超过有效期。')
    return redirect(url_for('main.index'))


@auth.before_app_request
def before_request():
    """限制未认证用户的活动范围"""
    if current_user.is_authenticated \
            and not current_user.confirmed \
            and request.endpoint \
            and request.endpoint[:5] != 'auth.' \
            and request.endpoint != 'static':
        return redirect(url_for('auth.unconfirmed'))

@auth.route('/unconfirmed')
def unconfirmed():
    """超出范围就转到提示页"""
    if current_user.is_anonymous or current_user.confirmed:
        return redirect(url_for('main.index'))
    return render_template('auth/unconfirmed.html')

@auth.route('/confirm')
@login_required
def resend_confirmation():
    """重新发送确认邮件"""
    token = current_user.generate_confirmation_token()
    send_email(current_user.email, 'Confirm Your Account',
               'auth/email/confirm', mailuser=current_user, token=token)
    flash('一封确认邮件已发送至您的邮箱。')
    return redirect(url_for('main.index'))

@auth.route('/changepassword', methods=['GET', 'POST'])
@login_required
def change_passwd():
    """修改密码"""
    changepw_app = ChangepwForm()
    if changepw_app.validate_on_submit():
        if current_user.verify_passwd(changepw_app.old_passwd_input.data):
            current_user.passwd = changepw_app.passwd_chg_input.data
            mydb.session.add(current_user)# pylint: disable=no-member
            mydb.session.commit()# pylint: disable=no-member
            flash('密码已修改。')
        else:
            flash('旧密码不正确。')
    return render_template('auth/changepassword.html', changepwform_display=changepw_app)

@auth.route('/reset', methods=['GET', 'POST'])
def password_reset_request():
    """重置密码申请"""
    if not current_user.is_anonymous:
        return redirect(url_for('main.index'))
    resetform_app = ResetrequestForm()
    if resetform_app.validate_on_submit():
        requestuser = User.query.filter_by(email=resetform_app.email_request_input.data).first()
        if requestuser:
            resettoken = requestuser.generate_resetpw_token()
            send_email(requestuser.email, '重设您的密码',
                       'auth/email/reset_password',
                       mailuser=requestuser, token=resettoken,
                       next=request.args.get('next'))
        flash('一封重设密码方法的邮件已发送到您的邮箱。')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password.html', resetform_display=resetform_app)

@auth.route('/reset/<token>', methods=['GET', 'POST'])
def password_reset(token):
    """修改密码页面"""
    if not current_user.is_anonymous:
        return redirect(url_for('main.index'))

    resetpwform_app = PasswordResetForm()

    #自动从token中储存的uid解析出用户邮箱
    s = Serializer(current_app.config['SECRET_KEY'])
    try:
        data = s.loads(token)
        resetid = data.get('reset')
        resetquery = User.query.filter_by(uid=resetid).first()
        resetpwform_app.email_resetpw_input.data = resetquery.email #设定email默认值且readonly
    except: # pylint: disable=W0702
        flash('您的url链接已失效。')
        return redirect(url_for('main.index'))

    if resetpwform_app.validate_on_submit():
        resetuser = User.query.filter_by(email=resetquery.email).first()
        if resetuser is None:
            return redirect(url_for('main.index'))
        if resetuser.reset_password(token, resetpwform_app.passwd_reset_input.data):
            flash('您的密码已修改。')
            return redirect(url_for('auth.login'))
        else:
            flash('您的密码未修改。')
            return redirect(url_for('main.index'))
    return render_template('auth/reset_password.html', resetform_display=resetpwform_app)
