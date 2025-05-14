from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_mysqldb import MySQL


login_manager = LoginManager()
bcrypt = Bcrypt()
mysql = MySQL()

def init_extensions(app):
    """Инициализирует все расширения приложения"""
    login_manager.init_app(app)
    bcrypt.init_app(app)
    
    # Настройка страницы входа
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Пожалуйста, войдите для доступа к этой странице'
    login_manager.login_message_category = 'info'