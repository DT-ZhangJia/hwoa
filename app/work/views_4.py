"""
固定资产视图
"""
# pylint: disable=invalid-name, too-few-public-methods
from datetime import datetime
from flask import render_template, redirect, url_for, flash, make_response
from flask_login import login_required, current_user
from flask_moment import Moment
import pytz
from sqlalchemy import and_, or_, not_
from .. import mydb
from .forms import LabelDict, DepreciationCalc
from . import work
from ..models import User, Departments, Assets


def monthgap(date1, date2):
    return date2.year*12 + date2.month - date1.year*12 - date1.month

@work.route('/depreciationcalc', methods=['GET', 'POST'])
@login_required
def depreciationcalc():
    """期间折旧计算"""

    depreciationcalc_app = DepreciationCalc()

    label_dict = LabelDict()
    account_dict = {1:"固定资产", 2:"在建工程", 3:"固定资产清理"}
    class_dict = {1:"房屋建筑", 2:"运输设备", 3:"机器设备", 4:"实验设备", 5:"通用设备"}
    #starttype_dict = {1:"新购待验收", 2:"验收设备转入", 3:"自建工程转入", 4:"修理工程转入",
    #                  5:"闲置启用", 6:"盘盈增加", 7:"改造工程转入", 8:"带折旧购入"}
    #endtype_dict = {1:"处置出售", 2:"验收开始使用", 3:"转到修理工程", 4:"转到闲置",
    #                5:"盘亏减少", 6:"转到改造工程", 7:"报废处置"}
    #place_dict = {1:"紫萍路", 2:"临沂", 3:"奉贤"}

    if depreciationcalc_app.validate_on_submit():

        all_dep = Assets.query.filter(not_(or_(Assets.isdep != 1,\
            Assets.termstart > depreciationcalc_app.enddate_dep_input.data,\
            and_(Assets.termend < depreciationcalc_app.startdate_dep_input.data,\
            Assets.termend != None)))).all()

        depresult = {}
        for i in range(1, 4):
            depresult[i] = {}
            for j in range(1, 16):
                depresult[i][j] = {1:0, 2:0, 3:0, 4:0, 5:0}

        """
        for asset in all_dep:
            if asset.termstart < depreciationcalc_app.startdate_dep_input.data:
                if asset.termend < depreciationcalc_app.enddate_dep_input.data:
                    start_dep = min((monthgap(depreciationcalc_app.startdate_dep_input.data, asset.termstart) * asset.monthdep + asset.syswithdep),(asset.originvalue - asset.netsalvage))
                    
                    asset_dep = 
            asset_dep = 1
            depresult[asset.companyid][asset.dptid][asset.classid] = depresult[asset.companyid][asset.dptid][asset.classid] + asset_dep # pylint: disable=C0301
        """

        return render_template('work/depcalcresult.html', depresult_disp=depresult,
                               all_dep_disp=all_dep, label_dict=label_dict,
                               account_dict=account_dict, class_dict=class_dict,
                               depreciationcalc_start=depreciationcalc_app.startdate_dep_input,
                               depreciationcalc_end=depreciationcalc_app.enddate_dep_input)

    return render_template('work/depcalcform.html', depreciationcalc_dsp=depreciationcalc_app)
