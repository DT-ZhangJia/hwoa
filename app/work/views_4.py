"""
固定资产视图
"""
# pylint: disable=invalid-name, too-few-public-methods
import datetime
from flask import render_template, redirect, url_for, flash, make_response
from flask_login import login_required
import pytz
from sqlalchemy import and_, or_, not_
from .. import mydb
from .forms import LabelDict, DepreciationCalc, Assetslist
from . import work
from ..models import User, Departments, Assets



def depmonth(start_date, end_date):
    """计算期间经过多少个1号——即折旧月数"""
    monthcalc = 0
    for n in range(int((end_date - start_date).days) + 1):
        date = start_date + datetime.timedelta(n)
        if date.day == 1:
            monthcalc = monthcalc + 1
    return monthcalc


@work.route('/depreciationcalc', methods=['GET', 'POST'])
@login_required
def depreciationcalc():
    """期间折旧计算"""


    depreciationcalc_app = DepreciationCalc()

    label_dict = LabelDict()
    account_dict = {1:"固定资产", 2:"在建工程", 3:"固定资产清理"}
    class_dict = {1:"房屋建筑", 2:"运输设备", 3:"机器设备", 4:"实验设备", 5:"通用设备"}
    #statustype_dict = {1:"初始计量", 2:"开始使用", 3:"开始计提", 4:"参数调整", 5:"终止确认"} #闲置也需要提折旧
    #endtype_dict = {1:"处置出售", 2:"验收开始使用", 3:"转入折旧状态", 4:"转到修理工程", 5:"转到闲置",
    #                6:"盘亏减少", 7:"转到改造工程", 8:"报废处置"} #闲置也需要提折旧
    #place_dict = {1:"紫萍路", 2:"临沂", 3:"奉贤"}

    #根据日期显示计提表格
    if depreciationcalc_app.validate_on_submit():

        #查询范围所有需计算折旧的记录
        all_dep = Assets.query.filter(not_(or_(Assets.isdep != 1,\
            Assets.termstart > depreciationcalc_app.enddate_dep_input.data,\
            and_(Assets.termend < depreciationcalc_app.startdate_dep_input.data,\
            Assets.termend != None)))).all()

        #准备空表格的字典
        depresult = {}
        for i in range(1, 4):#公司
            depresult[i] = {}
            for j in range(1, 16):#自设部门包含在建工程项目
                depresult[i][j] = {1:0, 2:0, 3:0, 4:0, 5:0}#类别

        #计算每个记录的折旧值并加到字典内
        for asset in all_dep:
            #确定计算的起止时点
            dep_startdate = datetime.date(1, 1, 1)
            dep_enddate = datetime.date(1, 1, 1)

            if depreciationcalc_app.startdate_dep_input.data >= asset.termstart:
                dep_startdate = depreciationcalc_app.startdate_dep_input.data
            else:
                dep_startdate = asset.termstart

            if asset.termend is None:
                dep_enddate = depreciationcalc_app.enddate_dep_input.data
            elif depreciationcalc_app.enddate_dep_input.data >= asset.termend:
                dep_enddate = asset.termend
            else:
                dep_enddate = depreciationcalc_app.enddate_dep_input.data

            #当期折旧计算值
            depcalc = depmonth(dep_startdate, dep_enddate) * asset.monthdep
            if (asset.syswithdep + depcalc) >= (asset.originvalue - asset.netsalvage):
                asset_dep = asset.originvalue - asset.netsalvage - asset.syswithdep
            else:
                asset_dep = depcalc
            depresult[asset.companyid][asset.dptid][asset.classid] = depresult[asset.companyid][asset.dptid][asset.classid] + asset_dep # pylint: disable=C0301


        return render_template('work/depcalcresult.html', depresult_disp=depresult,
                               all_dep_disp=all_dep, label_dict=label_dict,
                               account_dict=account_dict, class_dict=class_dict,
                               depreciationcalc_start=depreciationcalc_app.startdate_dep_input.data,
                               depreciationcalc_end=depreciationcalc_app.enddate_dep_input.data)


    return render_template('work/depcalcform.html', depreciationcalc_dsp=depreciationcalc_app)



@work.route('/assetslist', methods=['GET', 'POST'])
@login_required
def assetslist():
    """时点资产清单含累计折旧"""

    assetslist_app = Assetslist()

    assets_ondate_dict = {}

    if assetslist_app.validate_on_submit():
        #查找时点上的资产清单
        assets_ondate = Assets.query.filter(and_(Assets.termstart <= assetslist_app.listdate_al_input.data, #pylint: disable=C0301
                                                 or_(Assets.termend == None, #pylint: disable=C0121
                                                     Assets.termend >= assetslist_app.listdate_al_input.data))).all() #pylint: disable=C0301
        for asset in assets_ondate:
            substatus = Assets.query.filter(and_(Assets.syscode==asset.syscode, Assets.subcode<=asset.subcode, Assets.isdep==True)).all()
            dep_substatus = 0
            for sub in substatus:
                #确定计算的起止时点

                dep_enddate = datetime.date(1, 1, 1)

                if sub.termend is None:
                    dep_enddate = assetslist_app.listdate_al_input.data
                elif assetslist_app.listdate_al_input.data >= sub.termend:
                    dep_enddate = sub.termend
                else:
                    dep_enddate = assetslist_app.listdate_al_input.data

                #当期折旧计算值
                depcalc = depmonth(sub.termstart, dep_enddate) * sub.monthdep
                if (sub.syswithdep + depcalc) >= (sub.originvalue - sub.netsalvage):
                    asset_dep = sub.originvalue - sub.netsalvage - sub.syswithdep
                else:
                    asset_dep = depcalc

                dep_substatus = dep_substatus + asset_dep
            assets_ondate_dict[asset] = dep_substatus

        return render_template('work/assetslist.html',
                               listdate=assetslist_app.listdate_al_input.data,
                               assets_ondate_dict=assets_ondate_dict)

    return render_template('work/assetslistform.html', assetslist_dsp=assetslist_app)
