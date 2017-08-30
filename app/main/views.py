"""
learn flask views
"""
# pylint: disable=invalid-name, too-few-public-methods

#from datetime import datetime
#from flask import Flask, url_for, redirect, request, render_template, session, flash, current_app
from flask import render_template
from flask_login import login_required


from . import main
#from .forms import NameForm
#from .. import mydb
#from ..email import send_email
from ..models import User

"""

@main.route('/', methods=['GET', 'POST'])
def index():

    pyform = NameForm()
    if pyform.validate_on_submit():
        usercheck = User.query.filter_by(username=pyform.indexname.data).first()
        if usercheck is None:
            session['exist'] = False
            newuser = User(username=pyform.indexname.data, role_id=3)#建立新用户记录
            mydb.session.add(newuser)
            send_email(current_app.config['FLASKY_ADMIN'], 'New User',
                       'mail/new_user', mailuser=newuser)
        else:
            session['exist'] = True
        old_name = session.get('pyname')
        if old_name is not None and old_name != pyform.indexname.data:
            flash('name changed.')

        session['pyname'] = pyform.indexname.data
        pyform.indexname.data = ''
        return redirect(url_for('.index'))
    return render_template('index.html', indexform=pyform,
                           indexname2=session.get('pyname'),
                           exist_index=session.get('exist', False),
                           current_time=datetime.utcnow())

"""
@main.route('/')
def index():
    """index view"""
    return render_template('index.html')


@main.route('/ulist')
@login_required
def ulist():
    """user list"""
    all_user = User.query.all()
    return render_template('ulist.html', userlist=all_user)
