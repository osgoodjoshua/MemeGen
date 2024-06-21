from flask import render_template
from flask_login import login_required
from app.site import site_bp
from app.models import Image

@site_bp.route('/')
def home():
    images = Image.query.all()
    return render_template('home.html', images=images)

@site_bp.route('/meme')
@login_required
def meme():
    images = Image.query.all()
    return render_template('meme.html', images=images)
