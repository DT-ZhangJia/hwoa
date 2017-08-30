"""
learn flask auth
"""
# pylint: disable=invalid-name

from flask import Blueprint
auth = Blueprint('auth', __name__)
from . import views # pylint: disable=wrong-import-order, wrong-import-position
