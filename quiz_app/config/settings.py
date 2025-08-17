"""Application configuration settings."""
import os
from typing import Dict, Any

class Config:
    """Application configuration class."""
    
    # Database settings
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///quiz.db')
    DATABASE_PATH = os.getenv('DATABASE_PATH', 'quiz.db')
    
    # GUI settings
    WINDOW_WIDTH = 800
    WINDOW_HEIGHT = 600
    ADMIN_WINDOW_WIDTH = 1000
    ADMIN_WINDOW_HEIGHT = 700
    THEME = 'default'
    
    # Admin settings
    ADMIN_USERNAME = os.getenv('ADMIN_USERNAME', 'admin')
    ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', 'admin123')
    
    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', 'quiz_app.log')
    
    # Quiz settings
    DEFAULT_QUESTIONS_PER_QUIZ = 5
    
    # Quiz Timer Settings - CHỈ THỜI GIAN TỔNG
    TOTAL_QUIZ_TIME = 300  # seconds - 5 phút mặc định
    SHOW_TIMER = True  # Hiển thị đồng hồ đếm ngược
    AUTO_SUBMIT = True  # Tự động nộp bài khi hết giờ
    
    @classmethod
    def get_config(cls) -> Dict[str, Any]:
        """Get all configuration as dictionary."""
        return {
            'database_path': cls.DATABASE_PATH,
            'window_width': cls.WINDOW_WIDTH,
            'window_height': cls.WINDOW_HEIGHT,
            'admin_window_width': cls.ADMIN_WINDOW_WIDTH,
            'admin_window_height': cls.ADMIN_WINDOW_HEIGHT,
            'theme': cls.THEME,
            'log_level': cls.LOG_LEVEL,
            'log_file': cls.LOG_FILE,
            'default_questions_per_quiz': cls.DEFAULT_QUESTIONS_PER_QUIZ,
            'total_quiz_time': cls.TOTAL_QUIZ_TIME,
            'show_timer': cls.SHOW_TIMER,
            'auto_submit': cls.AUTO_SUBMIT
        }
    
    @classmethod
    def save_timer_settings(cls, total_quiz_time: int, show_timer: bool = True,
                           auto_submit: bool = True):
        """Save timer settings to config file."""
        import json
        config_file = 'quiz_config.json'
        
        settings = {
            'total_quiz_time': total_quiz_time,
            'show_timer': show_timer,
            'auto_submit': auto_submit
        }
        
        try:
            with open(config_file, 'w') as f:
                json.dump(settings, f, indent=4)
            
            # Update class variables
            cls.TOTAL_QUIZ_TIME = total_quiz_time
            cls.SHOW_TIMER = show_timer
            cls.AUTO_SUBMIT = auto_submit
            
            return True
        except Exception as e:
            print(f"Error saving config: {e}")
            return False
    
    @classmethod
    def load_timer_settings(cls):
        """Load timer settings from config file."""
        import json
        config_file = 'quiz_config.json'
        
        try:
            if os.path.exists(config_file):
                with open(config_file, 'r') as f:
                    settings = json.load(f)
                
                cls.TOTAL_QUIZ_TIME = settings.get('total_quiz_time', cls.TOTAL_QUIZ_TIME)
                cls.SHOW_TIMER = settings.get('show_timer', cls.SHOW_TIMER)
                cls.AUTO_SUBMIT = settings.get('auto_submit', cls.AUTO_SUBMIT)
        except Exception as e:
            print(f"Error loading config: {e}")

# Load settings khi khởi động
Config.load_timer_settings()