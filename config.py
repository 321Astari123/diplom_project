import os
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()

class Config:
    """Конфигурация приложения"""
    # Безопасность
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key')
    
    # База данных
    MYSQL_HOST = os.getenv('MYSQL_HOST', 'localhost')
    MYSQL_USER = os.getenv('MYSQL_USER', 'online_library_user')
    MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD', '12345678')
    MYSQL_DB = os.getenv('MYSQL_DB', 'online_library')
    
    # Загрузка файлов
    UPLOAD_FOLDER = 'static/uploads'
    COVER_FOLDER = os.getenv('COVER_FOLDER', 'static/covers')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    ALLOWED_EXTENSIONS = {'fb2', 'epub'}
    
    # Сессия
    SESSION_COOKIE_SECURE = False  # Изменено для работы в режиме разработки
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Другие настройки
    DEBUG = os.getenv('FLASK_ENV', 'development') == 'development'
    TESTING = False 