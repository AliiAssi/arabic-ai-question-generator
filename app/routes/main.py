from flask import Blueprint, render_template
from app.services.user_tracker import track_concurrent_users

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
@track_concurrent_users
def index():
    """Render the main page"""
    return render_template('index.html')