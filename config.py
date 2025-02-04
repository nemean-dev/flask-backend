import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Config:
    # customize the app
    POSTS_PER_PAGE = 12
    
    # securely sign data
    SECRET_KEY = os.getenv('SECRET_KEY') or \
        'random-hardcoded-string-102839yr1ewqouWsgYM3'
    
    # OpenAI API key for post translation
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    
    # db uri
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', '').replace(
        'postgres://', 'postgresql://') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    
    # Some deployments require logs to be sent to stdout
    LOG_TO_STDOUT = os.environ.get('LOG_TO_STDOUT')
    
    # email configuration
    MAIL_SERVER = os.getenv('MAIL_SERVER')
    MAIL_PORT = int(os.getenv('MAIL_PORT') or 25)
    MAIL_USE_TLS = os.getenv('MAIL_USE_TLS') is not None and os.getenv('MAIL_USE_TLS') != 0
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    ADMINS = os.getenv('MAIL_ADMINS').split(',') if os.getenv('MAIL_ADMINS') else None
    
    # supported languages
    LANGUAGES = ['en', 'es']

    # elasticsearch
    ELASTICSEARCH_URL = os.environ.get('ELASTICSEARCH_URL')