"""
权限视图模块
"""
# pylint: disable=invalid-name, too-few-public-methods
from flask import render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from flask_moment import Moment
from datetime import datetime
import pytz
from .. import mydb
from .forms import LabelDict, PayapplyForm, Paydetail, AddPermissionForm, Permissiondetail
from . import work
from ..models import Payments, Approvers, User, Permissions, Departments, Crossvalids, Lawyers
from sqlalchemy import and_, or_



@work.route('/addpermission', methods=['GET', 'POST'])
@login_required
def addpermission():
    """add new permission"""

    #刷新失效授权，效期末小于今天
    pytz.country_timezones('cn')
    tz = pytz.timezone('Asia/Shanghai')
    invalid_permissions = Permissions.query.filter(Permissions.termend<datetime.now(tz)).all()
    if invalid_permissions:
        for invalid in invalid_permissions:
            invalid.valid=False
            mydb.session.add(invalid)

    #动态初始化的表单实例
    mypermit = Permissions.query.filter(and_(Permissions.term==1, Permissions.puid==current_user.uid), Permissions.approved==1).order_by(Permissions.positionid).first()
    defaultinput=['']
    if mypermit:
        defaultinput.append(str(mypermit.apprv100001))
        defaultinput.append(str(mypermit.apprv100002))
        defaultinput.append(str(mypermit.apprv100003))
        defaultinput.append(str(mypermit.apprv100004))
        defaultinput.append(str(mypermit.apprv100005))
        defaultinput.append(str(mypermit.apprv100006))
        defaultinput.append(str(mypermit.apprv100007))
        defaultinput.append(str(mypermit.apprv100008))
        defaultinput.append(str(mypermit.apprv100009))
        defaultinput.append(str(mypermit.apprv100010))
        defaultinput.append(str(mypermit.apprv100011))
        defaultinput.append(str(mypermit.apprv100012))
        defaultinput.append(str(mypermit.apprv100013))
        defaultinput.append(str(mypermit.apprv100014))
        defaultinput.append(str(mypermit.apprv100015))
        defaultinput.append(str(mypermit.apprv100016))
        defaultinput.append(str(mypermit.apprv100017))
        defaultinput.append(str(mypermit.apprv100018))
        defaultinput.append(str(mypermit.apprv100019))
        addpermissionform_app = AddPermissionForm(apprv100001_addpm_input=defaultinput[1],
                                                  apprv100002_addpm_input=defaultinput[2],
                                                  apprv100003_addpm_input=defaultinput[3],
                                                  apprv100004_addpm_input=defaultinput[4],
                                                  apprv100005_addpm_input=defaultinput[5],
                                                  apprv100006_addpm_input=defaultinput[6],
                                                  apprv100007_addpm_input=defaultinput[7],
                                                  apprv100008_addpm_input=defaultinput[8],
                                                  apprv100009_addpm_input=defaultinput[9],
                                                  apprv100010_addpm_input=defaultinput[10],
                                                  apprv100011_addpm_input=defaultinput[11],
                                                  apprv100012_addpm_input=defaultinput[12],
                                                  apprv100013_addpm_input=defaultinput[13],
                                                  apprv100014_addpm_input=defaultinput[14],
                                                  apprv100015_addpm_input=defaultinput[15],
                                                  apprv100016_addpm_input=defaultinput[16],
                                                  apprv100017_addpm_input=defaultinput[17],
                                                  apprv100018_addpm_input=defaultinput[18],
                                                  apprv100019_addpm_input=defaultinput[19])
    else:
        flash('您无法进行授权。')
        return redirect(url_for('work.addrules'))

    #构建user选择器option传入模板
    selectoption_dict = {}
    label_dict = LabelDict()
    for key_i, _ in label_dict.all_company_dict.items():#公司遍历
        dptdict = {}
        for key_j,_ in label_dict.all_dpt_dict.items():#职能遍历
            userquery = User.query.filter(and_(User.company==key_i, User.dpt==key_j)).all()
            dptstr = ""
            for auser in userquery:
                dptstr = dptstr + "<option value='" + str(auser.uid) + "'>" + auser.name + "</option>"
            dptdict[key_j]=dptstr
        selectoption_dict[key_i]=dptdict

    apprv100001_data = 0.0
    apprv100002_data = 0.0
    apprv100003_data = 0.0
    apprv100004_data = 0.0
    apprv100005_data = 0.0
    apprv100006_data = 0.0
    apprv100007_data = 0.0
    apprv100008_data = 0.0
    apprv100009_data = 0.0
    apprv100010_data = 0.0
    apprv100011_data = 0.0
    apprv100012_data = 0.0
    apprv100013_data = 0.0
    apprv100014_data = 0.0
    apprv100015_data = 0.0
    apprv100016_data = 0.0
    apprv100017_data = 0.0
    apprv100018_data = 0.0
    apprv100019_data = 0.0
    #提交表单写入数据库
    addnewpower = False #创建权限的开关
    if addpermissionform_app.validate_on_submit():
        
        """
        #矫正时区（暂时屏蔽）
        pytz.country_timezones('cn')
        tz = pytz.timezone('Asia/Shanghai')
        """

        #判断当前用户的权限，长期董事长可以创建长临时；长期部门长可以创建临时
        """
        第一种模式符合ALL：
        1.授予职能=董事长
        2.授权期限=临时
        3.本人在权限表有权限且
        1）本人所属公司=授权范围公司
        2）本人权限为长期
        3）本人权限为董事长
        4）本人权限在效期内
        5）本人权限已审批且有效
        6）不能给自己授予临时董事长

        临时董事长可以有无数个，且不会相互迭代。
        """
        if (addpermissionform_app.position_addpm_input.data=="2" and
            addpermissionform_app.term_addpm_input.data=="2" and
            Permissions.query.filter(and_(Permissions.companyid==int(addpermissionform_app.company_addpm_input.data), 
            Permissions.term==1, Permissions.positionid==2, Permissions.termend>datetime.now(tz), Permissions.puid==current_user.uid, Permissions.approved==1, Permissions.valid==1)).all() and
            int(addpermissionform_app.user_addpm_input.data)!=current_user.uid):
            addnewpower = True #打开开关

        """
        第二种模式符合ALL：
        1.授予职能=部门长【且如果授予另一个人的授予时间与已有的长期部门长无交集】
        2.授权期限=长期
        3.本人在权限表有权限且
        1）本人所属公司=授权范围公司
        2）本人权限为长期
        3）本人权限为董事长
        4）本人权限在效期内
        5）本人权限已审批且有效

        长期部门长只能有一个，新增一个则前一个失效。
        """
        if (int(addpermissionform_app.position_addpm_input.data)>=4 and
            addpermissionform_app.term_addpm_input.data=="1" and
            Permissions.query.filter(and_(Permissions.companyid==int(addpermissionform_app.company_addpm_input.data), 
            Permissions.term==1, Permissions.positionid==2, Permissions.termend>datetime.now(tz), Permissions.puid==current_user.uid, Permissions.approved==1, Permissions.valid==1)).all()):
            addnewpower = True #打开开关

        """
        第三种模式符合ALL：
        1.授予职能=部门长
        2.授权期限=临时
        3.本人在权限表有权限且
        1）本人所属公司=授权范围公司
        2）本人权限为长期
        3）本人权限为部门长
        4）本人权限在效期内
        5）本人权限已审批且有效
        6）不能给自己授予临时部门长

        临时部门长只能有一个，新增一个则停用前一个。
        """
        if (int(addpermissionform_app.position_addpm_input.data)>=4 and
            addpermissionform_app.term_addpm_input.data=="2" and
            Permissions.query.filter(and_(Permissions.companyid==int(addpermissionform_app.company_addpm_input.data), 
            Permissions.term==1, Permissions.positionid==int(addpermissionform_app.position_addpm_input.data), Permissions.termend>datetime.now(tz), Permissions.puid==current_user.uid, Permissions.approved==1, Permissions.valid==1)).all() and
            int(addpermissionform_app.user_addpm_input.data)!=current_user.uid):
            addnewpower = True #打开开关

        #有效数据写入数据库
        if addnewpower == True:
            
            """
            判断所有权限金额超限
            """
            permit = Permissions.query.filter(and_(Permissions.companyid==int(addpermissionform_app.company_addpm_input.data), Permissions.term==1, Permissions.termend>datetime.now(tz), Permissions.puid==current_user.uid), Permissions.approved==1).first()

            if float(addpermissionform_app.apprv100001_addpm_input.data) > permit.apprv100001:
                apprv100001_data = permit.apprv100001
            else:
                apprv100001_data = float(addpermissionform_app.apprv100001_addpm_input.data)

            if float(addpermissionform_app.apprv100002_addpm_input.data) > permit.apprv100002:
                apprv100002_data = permit.apprv100002
            else:
                apprv100002_data = float(addpermissionform_app.apprv100002_addpm_input.data)

            if float(addpermissionform_app.apprv100003_addpm_input.data) > permit.apprv100003:
                apprv100003_data = permit.apprv100003
            else:
                apprv100003_data = float(addpermissionform_app.apprv100003_addpm_input.data)

            if float(addpermissionform_app.apprv100004_addpm_input.data) > permit.apprv100004:
                apprv100004_data = permit.apprv100004
            else:
                apprv100004_data = float(addpermissionform_app.apprv100004_addpm_input.data)

            if float(addpermissionform_app.apprv100005_addpm_input.data) > permit.apprv100005:
                apprv100005_data = permit.apprv100005
            else:
                apprv100005_data = float(addpermissionform_app.apprv100005_addpm_input.data)

            if float(addpermissionform_app.apprv100006_addpm_input.data) > permit.apprv100006:
                apprv100006_data = permit.apprv100006
            else:
                apprv100006_data = float(addpermissionform_app.apprv100006_addpm_input.data)

            if float(addpermissionform_app.apprv100007_addpm_input.data) > permit.apprv100007:
                apprv100007_data = permit.apprv100007
            else:
                apprv100007_data = float(addpermissionform_app.apprv100007_addpm_input.data)

            if float(addpermissionform_app.apprv100008_addpm_input.data) > permit.apprv100008:
                apprv100008_data = permit.apprv100008
            else:
                apprv100008_data = float(addpermissionform_app.apprv100008_addpm_input.data)

            if float(addpermissionform_app.apprv100009_addpm_input.data) > permit.apprv100009:
                apprv100009_data = permit.apprv100009
            else:
                apprv100009_data = float(addpermissionform_app.apprv100009_addpm_input.data)

            if float(addpermissionform_app.apprv100010_addpm_input.data) > permit.apprv100010:
                apprv100010_data = permit.apprv100010
            else:
                apprv100010_data = float(addpermissionform_app.apprv100010_addpm_input.data)

            if float(addpermissionform_app.apprv100011_addpm_input.data) > permit.apprv100011:
                apprv100011_data = permit.apprv100011
            else:
                apprv100011_data = float(addpermissionform_app.apprv100011_addpm_input.data)

            if float(addpermissionform_app.apprv100012_addpm_input.data) > permit.apprv100012:
                apprv100012_data = permit.apprv100012
            else:
                apprv100012_data = float(addpermissionform_app.apprv100012_addpm_input.data)

            if float(addpermissionform_app.apprv100013_addpm_input.data) > permit.apprv100013:
                apprv100013_data = permit.apprv100013
            else:
                apprv100013_data = float(addpermissionform_app.apprv100013_addpm_input.data)

            if float(addpermissionform_app.apprv100014_addpm_input.data) > permit.apprv100014:
                apprv100014_data = permit.apprv100014
            else:
                apprv100014_data = float(addpermissionform_app.apprv100014_addpm_input.data)

            if float(addpermissionform_app.apprv100015_addpm_input.data) > permit.apprv100015:
                apprv100015_data = permit.apprv100015
            else:
                apprv100015_data = float(addpermissionform_app.apprv100015_addpm_input.data)

            if float(addpermissionform_app.apprv100016_addpm_input.data) > permit.apprv100016:
                apprv100016_data = permit.apprv100016
            else:
                apprv100016_data = float(addpermissionform_app.apprv100016_addpm_input.data)

            if float(addpermissionform_app.apprv100017_addpm_input.data) > permit.apprv100017:
                apprv100017_data = permit.apprv100017
            else:
                apprv100017_data = float(addpermissionform_app.apprv100017_addpm_input.data)

            if float(addpermissionform_app.apprv100018_addpm_input.data) > permit.apprv100018:
                apprv100018_data = permit.apprv100018
            else:
                apprv100018_data = float(addpermissionform_app.apprv100018_addpm_input.data)

            if float(addpermissionform_app.apprv100019_addpm_input.data) > permit.apprv100019:
                apprv100019_data = permit.apprv100019
            else:
                apprv100019_data = float(addpermissionform_app.apprv100019_addpm_input.data)



            newpermission = Permissions(companyid=addpermissionform_app.company_addpm_input.data,
                                        positionid=addpermissionform_app.position_addpm_input.data,
                                        puid=addpermissionform_app.user_addpm_input.data,
                                        term=addpermissionform_app.term_addpm_input.data,
                                        termstart=addpermissionform_app.termstart_addpm_input.data,
                                        termend=addpermissionform_app.termend_addpm_input.data,
                                        originstart=addpermissionform_app.termstart_addpm_input.data,
                                        originend=addpermissionform_app.termend_addpm_input.data,
                                        approved=True,#这个开关等授权批准后改为False
                                        valid=True,#用于控制有效无效
                                        apprv100001=apprv100001_data,
                                        apprv100002=apprv100002_data,
                                        apprv100003=apprv100003_data,
                                        apprv100004=apprv100004_data,
                                        apprv100005=apprv100005_data,
                                        apprv100006=apprv100006_data,
                                        apprv100007=apprv100007_data,
                                        apprv100008=apprv100008_data,
                                        apprv100009=apprv100009_data,
                                        apprv100010=apprv100010_data,
                                        apprv100011=apprv100011_data,
                                        apprv100012=apprv100012_data,
                                        apprv100013=apprv100013_data,
                                        apprv100014=apprv100014_data,
                                        apprv100015=apprv100015_data,
                                        apprv100016=apprv100016_data,
                                        apprv100017=apprv100017_data,
                                        apprv100018=apprv100018_data,
                                        apprv100019=apprv100019_data)

            if current_user.uid == 1: #董事长创建的记录都自动生效
                newpermission.approved=True
                newpermission.valid=True

            #这里要处理旧授权人的时效问题
            oldpermissions = Permissions.query.filter(and_(Permissions.companyid==addpermissionform_app.company_addpm_input.data,
                                                            Permissions.positionid==addpermissionform_app.position_addpm_input.data,
                                                            Permissions.positionid!=2,#排除董事长，限定部门长唯一
                                                            #Permissions.term==addpermissionform_app.term_addpm_input.data,
                                                            Permissions.termend>addpermissionform_app.termstart_addpm_input.data,
                                                            Permissions.termstart<addpermissionform_app.termend_addpm_input.data)).all()
            pytz.country_timezones('cn')
            tz = pytz.timezone('Asia/Shanghai')
            for old in oldpermissions:
                if ((int(addpermissionform_app.term_addpm_input.data)==1 and 
                     old.puid==int(addpermissionform_app.user_addpm_input.data) and
                     old.term==2) or old.term==int(addpermissionform_app.term_addpm_input.data)):
                    old.termend = addpermissionform_app.termstart_addpm_input.data
                    if datetime.combine(addpermissionform_app.termstart_addpm_input.data, datetime.min.time()).replace(tzinfo=tz)<=datetime.now(tz):#如果新建授权立刻生效的话就停用其他
                        old.valid = False
                    if old.termstart > datetime.combine(old.termend, datetime.min.time()):#防止出现时间倒挂
                        old.termstart = old.termend
                    mydb.session.add(old)

            mydb.session.add(newpermission)# pylint: disable=no-member
            mydb.session.commit()# pylint: disable=no-member 需要立刻提交数据库以获得id
            flash('授权书已生成。')
            return redirect(url_for('work.permissionlist'))

        else:
            flash('您无法进行此项授权。')

    return render_template('work/addpermission.html', addpermissionform_display=addpermissionform_app, selectoption_dict=selectoption_dict, addnewpower=addnewpower,apprv100001_data=apprv100001_data)


@work.route('/permissionlist')
@login_required
def permissionlist():
    """授权列表"""
    all_permissions = Permissions.query.filter_by(approved=True)
    label_dict = LabelDict()

    #刷新失效授权，效期末小于今天
    pytz.country_timezones('cn')
    tz = pytz.timezone('Asia/Shanghai')
    invalid_permissions = Permissions.query.filter(Permissions.termend<datetime.now(tz)).all()
    if invalid_permissions:
        for invalid in invalid_permissions:
            invalid.valid=False
            mydb.session.add(invalid)
        

    return render_template('work/permissionlist.html', 
                           permissionlist=all_permissions, 
                           label_dict=label_dict)



@work.route('/permissiondetail/<pmid>', methods=['GET', 'POST'])
@login_required
def permissiondetail(pmid):
    """授权详情页"""
    permissiondetail_app = Permissiondetail()
    permissiondetail_query = Permissions.query.filter_by(idpermission=pmid).first()

    if permissiondetail_query is None:
        return render_template('404.html'), 404

    else:
        permituser = User.query.filter_by(uid=permissiondetail_query.puid).first()
        #准备数据
        label_dict = LabelDict() #数据字典实例
        companydict = label_dict.all_company_dict #公司字典
        dptdict = label_dict.all_dpt_dict #部门字典
        positiondict = label_dict.all_dptincharge_dict #职能字典
        allusersdict = label_dict.all_users_dict #人员姓名字典

        #填充数据
        permissiondetail_app.idpermission_pmdt_input.data = "[授权书] "+str(permissiondetail_query.idpermission)+" 号"
        permissiondetail_app.company_pmdt_input.data = companydict[permissiondetail_query.companyid]
        permissiondetail_app.position_pmdt_input.data = positiondict[permissiondetail_query.positionid]
        permissiondetail_app.usercompany_pmdt_input.data = companydict[permituser.company]
        permissiondetail_app.userdpt_pmdt_input.data = dptdict[permituser.dpt]
        permissiondetail_app.user_pmdt_input.data = allusersdict[permissiondetail_query.puid]
        permissiondetail_app.term_pmdt_input.data = {1:"长期",2:"临时"}[permissiondetail_query.term]
        permissiondetail_app.termstart_pmdt_input.data = permissiondetail_query.termstart
        permissiondetail_app.termend_pmdt_input.data = permissiondetail_query.termend
        permissiondetail_app.originstart_pmdt_input.data = permissiondetail_query.originstart
        permissiondetail_app.originend_pmdt_input.data = permissiondetail_query.originend
        permissiondetail_app.valid_pmdt_input.data = {True:"生效中",False:"已失效"}[permissiondetail_query.valid]
        permissiondetail_app.apprv100001_pmdt_input.data = permissiondetail_query.apprv100001
        permissiondetail_app.apprv100002_pmdt_input.data = permissiondetail_query.apprv100002
        permissiondetail_app.apprv100003_pmdt_input.data = permissiondetail_query.apprv100003
        permissiondetail_app.apprv100004_pmdt_input.data = permissiondetail_query.apprv100004
        permissiondetail_app.apprv100005_pmdt_input.data = permissiondetail_query.apprv100005
        permissiondetail_app.apprv100006_pmdt_input.data = permissiondetail_query.apprv100006
        permissiondetail_app.apprv100007_pmdt_input.data = permissiondetail_query.apprv100007
        permissiondetail_app.apprv100008_pmdt_input.data = permissiondetail_query.apprv100008
        permissiondetail_app.apprv100009_pmdt_input.data = permissiondetail_query.apprv100009
        permissiondetail_app.apprv100010_pmdt_input.data = permissiondetail_query.apprv100010
        permissiondetail_app.apprv100011_pmdt_input.data = permissiondetail_query.apprv100011
        permissiondetail_app.apprv100012_pmdt_input.data = permissiondetail_query.apprv100012
        permissiondetail_app.apprv100013_pmdt_input.data = permissiondetail_query.apprv100013
        permissiondetail_app.apprv100014_pmdt_input.data = permissiondetail_query.apprv100014
        permissiondetail_app.apprv100015_pmdt_input.data = permissiondetail_query.apprv100015
        permissiondetail_app.apprv100016_pmdt_input.data = permissiondetail_query.apprv100016
        permissiondetail_app.apprv100017_pmdt_input.data = permissiondetail_query.apprv100017
        permissiondetail_app.apprv100018_pmdt_input.data = permissiondetail_query.apprv100018
        permissiondetail_app.apprv100019_pmdt_input.data = permissiondetail_query.apprv100019


        return render_template('work/permissiondetail.html', permissiondetail_disp=permissiondetail_app)


@work.route('/addrules')
@login_required
def addrules():
    """授权规则说明及consultant列表"""

    pytz.country_timezones('cn')
    tz = pytz.timezone('Asia/Shanghai')

    label_dict = LabelDict()
    
    #只需要实际部门信息
    realdpt_dict = {}
    for key, value in label_dict.all_dpt_dict.items():
        if key >= 4:
            realdpt_dict[key] = value
    
    #刷新失效授权，效期末小于今天
    pytz.country_timezones('cn')
    tz = pytz.timezone('Asia/Shanghai')
    invalid_permissions = Permissions.query.filter(Permissions.termend<datetime.now(tz)).all()
    if invalid_permissions:
        for invalid in invalid_permissions:
            invalid.valid=False
            mydb.session.add(invalid)

    #部门负责人表格数据
    incharge_all = Permissions.query.filter(and_(Permissions.approved==True,\
        Permissions.valid==True, Permissions.termstart<=datetime.now(tz),\
        Permissions.termend>=datetime.now(tz))).all()
    cv_all = Crossvalids.query.order_by(Crossvalids.crossdpt).all()

    rule_dict = {}
    uidlist = []
    for key_i, _ in label_dict.all_company_dict.items():
        dpt_dict = {}
        for key_j, _ in realdpt_dict.items():
            uidlist = [cv.crossuid for cv in cv_all if cv.companyid==key_i and cv.crossdpt==key_j]
            ichlist = [incharge.puid for incharge in incharge_all if incharge.companyid==key_i and incharge.positionid==key_j]
            dpt_dict[key_j] = [ichlist,uidlist]
        rule_dict[key_i] = dpt_dict

    #法务财务表格数据
    lawyers = Lawyers.query.all()
    lawyer_dict = {}
    lawuidlist = []
    accuidlist = []
    for key, _ in label_dict.all_company_dict.items():
        lawuidlist = [lawyer.consultantuid for lawyer in lawyers if lawyer.companyid==key and lawyer.consultant==1]
        accuidlist = [acc.consultantuid for acc in lawyers if acc.companyid==key and acc.consultant==2]
        lawyer_dict[key] = [lawuidlist,accuidlist]

    return render_template('work/addrules.html', label_dict=label_dict, rule_dict=rule_dict, lawyer_dict=lawyer_dict)