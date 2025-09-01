import os
from datetime import timedelta

class Config:
    """Base configuration class."""
    
    # Flask settings
    SECRET_KEY = os.environ.get('SESSION_SECRET') or 'dev-secret-key-change-in-production'
    
    # Database settings
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///tradesos.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_recycle': 300,
        'pool_pre_ping': True,
    }
    
    # File upload settings
    UPLOAD_FOLDER = 'uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    
    # Mail settings
    MAIL_SERVER = os.environ.get('MAIL_SERVER') or 'localhost'
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 587)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER') or 'noreply@tradesos.co.uk'
    
    # Stripe settings
    STRIPE_SECRET_KEY = os.environ.get('STRIPE_SECRET_KEY')
    STRIPE_PUBLISHABLE_KEY = os.environ.get('STRIPE_PUBLISHABLE_KEY')
    STRIPE_WEBHOOK_SECRET = os.environ.get('STRIPE_WEBHOOK_SECRET')
    
    # TradeSOS specific settings
    PREMIUM_FIRST_ACCESS_MINUTES = int(os.environ.get('PREMIUM_FIRST_ACCESS_MINUTES') or 3)
    TRACKING_PING_INTERVAL_SEC = int(os.environ.get('TRACKING_PING_INTERVAL_SEC') or 15)
    TRACKING_RETENTION_HOURS = int(os.environ.get('TRACKING_RETENTION_HOURS') or 24)
    AVG_TRAVEL_SPEED_KMH = int(os.environ.get('AVG_TRAVEL_SPEED_KMH') or 30)
    ENABLE_RADIUS_FILTER = os.environ.get('ENABLE_RADIUS_FILTER', 'false').lower() == 'true'
    
    # Subscription pricing (in pence)
    STANDARD_PLAN_PRICE = 4000  # £40.00
    PREMIUM_PLAN_PRICE = 8000   # £80.00
    
    # Application settings
    BASE_URL = os.environ.get('BASE_URL') or 'http://localhost:5000'
    ENABLE_EMAIL_NOTIFICATIONS = os.environ.get('ENABLE_EMAIL_NOTIFICATIONS', 'true').lower() == 'true'
    
    # Session settings
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    
    # Security settings
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = None
    
    # Pagination
    POSTS_PER_PAGE = 20
    TRADES_PER_PAGE = 12
    JOBS_PER_PAGE = 10

class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///tradesos_dev.db'

class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    
    # Use PostgreSQL in production
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'postgresql://username:password@localhost/tradesos'
    
    # Enhanced security settings
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'

class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False
    ENABLE_EMAIL_NOTIFICATIONS = False

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
