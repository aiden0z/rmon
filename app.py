""" app.py

应用入口文件
"""
import urllib
from rmon.app import create_app
from rmon.models import User
from rmon.extensions import db

app = create_app()

@app.cli.command()
def routes():
    """输出 app 中定义的所有路由
    """
    output = []
    for rule in app.url_map.iter_rules():
        methods = ','.join(rule.methods)
        line = urllib.parse.unquote("{:25s} {:35s} {:20s}".format(
            rule.endpoint, methods, str(rule)))
        output.append(line)

    for line in sorted(output):
        print(line)


@app.cli.command()
def init_db():
    """初始化数据库
    """
    db.create_all()
    print("sqlite3 database file is %s" % app.config['SQLALCHEMY_DATABASE_URI'])

    # create administrator
    name, password = User.create_administrator()

    # 如果 password 为空，代表已经存在 admin 账户
    if password != '':
        print("create admin user %s with password %s" % (name, password))
