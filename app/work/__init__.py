"""
learn flask work
"""
# pylint: disable=invalid-name

from flask import Blueprint
work = Blueprint('work', __name__)
from . import views_1, views_2 # pylint: disable=wrong-import-order, wrong-import-position
