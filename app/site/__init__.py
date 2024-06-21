from flask import Blueprint

site_bp = Blueprint('site', __name__)

from app.site import routes
