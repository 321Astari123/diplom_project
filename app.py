from flask import Flask
from flask_login import LoginManager
from modules.database import init_db, create_tables
from modules import profile_bp, books_bp, auth_bp, admin_bp
import logging

# Настройка логирования
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')
    
    # Инициализация базы данных
    init_db()
    create_tables()
    
    # Настройка Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    
    # Регистрация blueprints
    app.register_blueprint(profile_bp)
    app.register_blueprint(books_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    
    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0') 