# Redis Monitor System Sample

Based on Flask + Restful API + Vue.js.

## Start

Install python packages:

```bash
$ virtualenv venv
$ source venv/bin/activate
$ pip install -r requirements.txt
```

Then start project:

```bash
$ FLASK_APP=app.py flask run
```

Now you can access project at `http://127.0.0.1:5000`.

## Testcase

You can use below command to run project testcase:

```
$ cd tests
$ py.test
```

**The redis server should be running at 127.0.0.1:6379 without password before run testcase.**


