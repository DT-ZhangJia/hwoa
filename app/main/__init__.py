"""
learn flask blueprint factory
"""
# pylint: disable=invalid-name


from flask import Blueprint

main = Blueprint('main', __name__)

#防止循环导入把这堆东西放在最后
from .import views, errors # pylint: disable=wrong-import-position
