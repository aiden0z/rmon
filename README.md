# DevOps 示例项目 - 简单的 Redis 实时监控系统

## 启动应用

基于 Python3 开发，通过 virtualenv 建立开发环境

```
$ virtualenv venv
$ source venv/bin/activate
$ pip install -r requirements.txt
```

依赖软件包安装完成后，通过以下命令启动应用：

```
$ FLASK_APP=app.py flask run
```

接着访问 `http://127.0.0.1:5000` 查看效果。

## 测试用例

通过 virtualenv 建立依赖环境并激活后，通过下面的命令运行测试用例:

```
$ cd tests
$ py.test
```

注意：运行测试用例时，要求本机已安装 Redis 服务器，监听在 127.0.0.1:6379 地址，且不需要密码访问。
