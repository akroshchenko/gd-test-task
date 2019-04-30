# -*- coding: utf-8 -*-

'''Just module docstring'''

import json
import random
from datetime import datetime
from functools import wraps
from uuid import uuid4

from flask import Flask, abort, request


class User:
    '''Initialize user'''

    def __init__(self, name, password):
        '''Constructor'''

        self.name = name
        self.password = password
        self.token = None
        self.login_time = None

    def login(self, name, password):
        '''Generates temp token'''

        if self.name == name and self.password == password:
            self.token = str(uuid4())
            self.login_time = datetime.now()
            return True

        return False


class Task:
    '''Initialize Task'''

    def __init__(self):
        '''Constructor'''

        self.state = "waiting"
        self.log = ""
        self.result = 0

    def Run(self):
        '''Change task state'''

        random.seed()

        self.state = random.choice(["ok", "notOk"])

        if self.state == "ok":
            self.result = random.randint(1, 10)
        else:
            self.log = "Critical issue"


ADMIN = User("admin", "admin")
TASK = Task()

app = Flask(__name__)


def require_api_token(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if request.args.get('api_token') and request.args.get('api_token') == ADMIN.token:
            if (datetime.now() - ADMIN.login_time).seconds < 300:
                return f(*args, **kwargs)

        return abort(403)

    return decorated


@app.route('/apitoken', methods=['POST'])
def login():

    r_user = request.args.get("user")
    r_pass = request.args.get("password")

    r_data = f"Wrong creds. {r_user}:{r_pass} is wrond user:pass combination"

    if ADMIN.login(r_user, r_pass):
        r_data = {"token": ADMIN.token}

    return app.response_class(
        response=json.dumps(r_data),
        status=404,
        mimetype='application/json'
    )


@app.route("/task", methods=['GET'])
@require_api_token
def get_task_status():

    if TASK.state == "waiting":
        r_status = 404
        r_data = "Not found"
    elif TASK.state == "ok":
        r_status = 200
        r_data = f"RESULT:{TASK.result}"
    else:
        r_status = 500
        r_data = f"ERROR:{TASK.log}"

    return app.response_class(
        response=json.dumps(r_data),
        status=r_status,
        mimetype='application/json'
    )


@app.route("/task/start", methods=['POST'])
@require_api_token
def start_task():

    TASK.Run()

    return app.response_class(
        response=json.dumps({"message": "Task has been started"}),
        status=200,
        mimetype='application/json'
    )


if __name__ == "__main__":
    app.run()
