from flask import Blueprint, jsonify
from app.services.user_tracker import user_tracker, track_concurrent_users

system_api = Blueprint('system_api', __name__)

# will be injected from app
config = None

def init_system_api(app_config):
    """Initialize the API with required configuration"""
    global config
    config = app_config

@system_api.route('/health', methods=['GET'])
@track_concurrent_users
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'ai-content-generator',
        'max_workers': config.max_workers,
        'concurrent_users': user_tracker.get_concurrent_users_count()
    })

@system_api.route('/stats', methods=['GET'])
@track_concurrent_users
def stats():
    """Get detailed user statistics"""
    stats = user_tracker.get_detailed_stats()
    return jsonify(stats)