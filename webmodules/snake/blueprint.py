from flask import render_template, Blueprint
from .._main import app

blue = Blueprint(
    'snake', 
    __name__, 
    url_prefix = '/snake',
    template_folder = 'templates',
    static_folder = 'static',
    static_url_path = '/snakesource',
)

@blue.route('/', methods = ['GET'])
def root():
    return render_template('snake.html')


app.register_blueprint(blue)