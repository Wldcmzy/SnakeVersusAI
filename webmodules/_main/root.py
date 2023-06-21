from flask import Flask, request, session, redirect
from flask_socketio import SocketIO
from flask_cors import CORS
import os
from .config import GLOBAL_INTERCEPT
from .blueprint import blue
from .identify import *

ws = SocketIO()
app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
CORS(app, supports_credentials=True)
app.register_blueprint(blue)


@app.before_request
def before():
    if GLOBAL_INTERCEPT:
        url = request.path
        if not judge_pass_url(url):
            username = session.get('username', None)
            cookie = session.get('cookie', None)
            if not cookie or not check_cookie(username, cookie):
                return redirect('/login')





