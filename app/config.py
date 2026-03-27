import os


class Config:
    """Base configuration"""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-key-change-in-production')
    LOGS_PATH = os.environ.get('MATTERLOGSERVER_LOGS_PATH', './logs')
    LOGS_BASE_URL = os.environ.get('MATTERLOGSERVER_LOGS_BASE_URL', '')
    PROXY_LEVEL = int(os.environ.get('MATTERLOGSERVER_PROXY_LEVEL', 0))


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False


class TestingConfig(Config):
    TESTING = True
    LOGS_PATH = './tests/data/logs'


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
