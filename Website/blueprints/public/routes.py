from flask import render_template, Blueprint
public_bp = Blueprint('public', __name__, template_folder='templates/public')

@public_bp.route('/')
def index():
    return render_template('index.html')

@public_bp.route('/about')
def about():
    return render_template('about.html')

@public_bp.route('/contact')
def contact():
    return render_template('contact.html')
