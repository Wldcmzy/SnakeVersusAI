from flask import (
    Blueprint, 
    request, 
    session, 
    redirect, 
    render_template, 
    send_from_directory,
)
from .identify import *

blue = Blueprint(
    'main', 
    __name__, 
    url_prefix = '/',
    template_folder = 'templates',
    static_folder = 'static',
    static_url_path = '/',
)

@blue.route('/')
def home():
    return render_template('home.html')

@blue.route('/favicon.ico')
def ikun():
    return send_from_directory('static', 'favicon.ico')

@blue.route('/login', methods = ['POST', 'GET'])
def login():
    if request.method == 'POST':
        form = request.form
        username = form.get('username')
        password = form.get('password')
        if identify(username, password):
            cookie = Cookie()
            cookie_dict[username] = cookie
            session['username'] = username
            session['cookie'] = cookie.value
            return redirect('/')
        else:
            return redirect('/login')
    else:
        return render_template("login.html")