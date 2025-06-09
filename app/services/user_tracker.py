import logging
import threading
import time
from datetime import datetime
from typing import Dict, Set
from dataclasses import dataclass
from flask import request, session
import uuid
import json
import os

@dataclass
class UserSession:
    session_id: str
    ip_address: str
    user_agent: str
    first_seen: datetime
    last_seen: datetime
    page_views: int = 0
    requests_count: int = 0

class ConcurrentUserTracker:
    """Track concurrent users and log statistics"""
    
    def __init__(self, log_file_path: str = "logs/concurrent_users.log"):
        self.active_sessions: Dict[str, UserSession] = {}
        self.lock = threading.Lock()
        self.log_file_path = log_file_path
        self.cleanup_interval = 300  # 5 minutes
        self.session_timeout = 1800  # 30 minutes
        
        # Setup logging
        self._setup_logging()
        
        # Start cleanup thread
        self.cleanup_thread = threading.Thread(target=self._cleanup_inactive_sessions, daemon=True)
        self.cleanup_thread.start()
        
        # Start periodic logging thread
        self.stats_thread = threading.Thread(target=self._log_periodic_stats, daemon=True)
        self.stats_thread.start()
    
    def _setup_logging(self):
        """Setup logging configuration"""
        # Create logs directory if it doesn't exist
        os.makedirs(os.path.dirname(self.log_file_path), exist_ok=True)
        
        # Setup concurrent users logger
        self.logger = logging.getLogger('concurrent_users')
        self.logger.setLevel(logging.INFO)
        
        # File handler for concurrent users log
        file_handler = logging.FileHandler(self.log_file_path, encoding='utf-8')
        file_handler.setLevel(logging.INFO)
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s | %(levelname)s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(formatter)
        
        # Add handler to logger
        if not self.logger.handlers:
            self.logger.addHandler(file_handler)
        
        # Setup detailed activity logger
        self.activity_logger = logging.getLogger('user_activity')
        self.activity_logger.setLevel(logging.INFO)
        
        activity_file_handler = logging.FileHandler('logs/user_activity.log', encoding='utf-8')
        activity_file_handler.setFormatter(formatter)
        
        if not self.activity_logger.handlers:
            self.activity_logger.addHandler(activity_file_handler)
    
    def track_user_request(self, endpoint: str = None):
        """Track a user request and update session info"""
        try:
            # Get or create session ID
            if 'session_id' not in session:
                session['session_id'] = str(uuid.uuid4())
            
            session_id = session['session_id']
            current_time = datetime.now()
            ip_address = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
            user_agent = request.headers.get('User-Agent', 'Unknown')
            
            with self.lock:
                if session_id in self.active_sessions:
                    # Update existing session
                    user_session = self.active_sessions[session_id]
                    user_session.last_seen = current_time
                    user_session.requests_count += 1
                    if endpoint == '/':
                        user_session.page_views += 1
                else:
                    # Create new session
                    user_session = UserSession(
                        session_id=session_id,
                        ip_address=ip_address,
                        user_agent=user_agent,
                        first_seen=current_time,
                        last_seen=current_time,
                        page_views=1 if endpoint == '/' else 0,
                        requests_count=1
                    )
                    self.active_sessions[session_id] = user_session
                    
                    # Log new user connection
                    self.logger.info(f"NEW_USER | Session: {session_id[:8]}... | IP: {ip_address} | Total Active: {len(self.active_sessions)}")
                
                # Log request activity
                if endpoint:
                    self.activity_logger.info(f"REQUEST | Session: {session_id[:8]}... | IP: {ip_address} | Endpoint: {endpoint} | Active Users: {len(self.active_sessions)}")
        
        except Exception as e:
            print(f"Error tracking user: {e}")
    
    def get_concurrent_users_count(self) -> int:
        """Get current number of concurrent users"""
        with self.lock:
            return len(self.active_sessions)
    
    def get_detailed_stats(self) -> Dict:
        """Get detailed statistics about active users"""
        with self.lock:
            current_time = datetime.now()
            stats = {
                'total_active_users': len(self.active_sessions),
                'timestamp': current_time.isoformat(),
                'users_by_timeframe': {
                    'last_1_min': 0,
                    'last_5_min': 0,
                    'last_15_min': 0,
                    'last_30_min': 0
                },
                'total_page_views': sum(session.page_views for session in self.active_sessions.values()),
                'total_requests': sum(session.requests_count for session in self.active_sessions.values()),
                'unique_ips': len(set(session.ip_address for session in self.active_sessions.values()))
            }
            
            # Calculate users by timeframe
            for session in self.active_sessions.values():
                time_diff = (current_time - session.last_seen).total_seconds()
                if time_diff <= 60:
                    stats['users_by_timeframe']['last_1_min'] += 1
                if time_diff <= 300:
                    stats['users_by_timeframe']['last_5_min'] += 1
                if time_diff <= 900:
                    stats['users_by_timeframe']['last_15_min'] += 1
                if time_diff <= 1800:
                    stats['users_by_timeframe']['last_30_min'] += 1
            
            return stats
    
    def _cleanup_inactive_sessions(self):
        """Remove inactive sessions periodically"""
        while True:
            try:
                time.sleep(self.cleanup_interval)
                current_time = datetime.now()
                inactive_sessions = []
                
                with self.lock:
                    for session_id, user_session in list(self.active_sessions.items()):
                        time_diff = (current_time - user_session.last_seen).total_seconds()
                        if time_diff > self.session_timeout:
                            inactive_sessions.append(session_id)
                            del self.active_sessions[session_id]
                
                # Log cleanup results
                if inactive_sessions:
                    self.logger.info(f"CLEANUP | Removed {len(inactive_sessions)} inactive sessions | Active Users: {len(self.active_sessions)}")
                    
            except Exception as e:
                print(f"Error in cleanup thread: {e}")
    
    def _log_periodic_stats(self):
        """Log statistics periodically"""
        while True:
            try:
                time.sleep(60)  # Log every minute
                stats = self.get_detailed_stats()
                
                self.logger.info(
                    f"STATS | Active: {stats['total_active_users']} | "
                    f"Last 1min: {stats['users_by_timeframe']['last_1_min']} | "
                    f"Last 5min: {stats['users_by_timeframe']['last_5_min']} | "
                    f"Unique IPs: {stats['unique_ips']} | "
                    f"Total Requests: {stats['total_requests']} | "
                    f"Page Views: {stats['total_page_views']}"
                )
                
            except Exception as e:
                print(f"Error in stats logging thread: {e}")
    
    def export_stats_to_json(self, file_path: str = "logs/user_stats.json"):
        """Export current stats to JSON file"""
        try:
            stats = self.get_detailed_stats()
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(stats, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error exporting stats: {e}")
            return False

# Singleton instance
user_tracker = ConcurrentUserTracker()

# Flask middleware decorator
def track_concurrent_users(f):
    """Decorator to track concurrent users for Flask routes"""
    def decorated_function(*args, **kwargs):
        user_tracker.track_user_request(request.endpoint)
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function