""" rmon.views.urls

定义了所有 API 对应的 URL
"""
from flask import Blueprint

from rmon.views.index import IndexView

api = Blueprint('api', __name__)

api.add_url_rule('/', view_func=IndexView.as_view('index'))