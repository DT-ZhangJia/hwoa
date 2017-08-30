"""
learn flask views
"""
# pylint: disable=invalid-name, too-few-public-methods

#from flask import Flask, url_for, redirect, request, render_template, session, flash
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import Required

class NameForm(FlaskForm):
    """NameForm"""
    indexname = StringField('填写你的ID：', validators=[Required()]) #NameForm类的所有实例共享该变量
    #indexpass = PasswordField('密码：', validators=[Required()])
    indexsubmit = SubmitField('提交') #NameForm类的所有实例共享该变量
