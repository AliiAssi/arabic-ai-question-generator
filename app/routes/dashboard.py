from flask import Blueprint, render_template, jsonify
from app.services.user_tracker import user_tracker, track_concurrent_users

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/admin')

@dashboard_bp.route('/dashboard')
@track_concurrent_users
def admin_dashboard():
    """Admin dashboard to view concurrent users"""
    # In production, add authentication here
    return render_template('admin_dashboard.html')

@dashboard_bp.route('/users', methods=['GET'])
@track_concurrent_users
def admin_users():
    """Admin endpoint to view current active users"""
    # In production, add authentication here
    stats = user_tracker.get_detailed_stats()
    return jsonify({
        'current_stats': stats,
        'message': 'Active users monitoring'
    })