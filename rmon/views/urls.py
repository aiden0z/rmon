""" rmon.views.urls

定义了所有 API 对应的 URL
"""
from flask import Blueprint

from rmon.views.index import IndexView
from rmon.views.server import (ServerCommand, ServerDetail, ServerList,
                               ServerMetrics)

api = Blueprint('api', __name__)

api.add_url_rule('/', view_func=IndexView.as_view('index'))

api.add_url_rule('/servers/',
                 view_func=ServerList.as_view('server_list'))
api.add_url_rule('/servers/<int:object_id>', 
                 view_func=ServerDetail.as_view('server_detail'))
api.add_url_rule('/servers/<int:object_id>/metrics', 
                 view_func=ServerMetrics.as_view('server_metrics'))
api.add_url_rule('/servers/<int:object_id>/command',
                 view_func=ServerCommand.as_view('server_command'))
