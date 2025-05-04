from flask import Flask, redirect, url_for
from flask_login import LoginManager
from modules.database import init_db
from extensions import init_extensions
from modules.models import User
from modules.auth import auth_bp
from modules.books import books_bp
from modules.admin import admin_bp
import os


def create_app():
    """Создает и настраивает приложение Flask"""
    app = Flask(__name__)
    
    # Загрузка конфигурации
    app.config.from_object('config.Config')
    
    # Инициализация расширений
    init_extensions(app)
    
    # Инициализация базы данных
    app.mysql = init_db(app)
    
    # Регистрация blueprints
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(books_bp, url_prefix='/books')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    
    # Создание директорий для загрузки файлов
    os.makedirs(os.path.join(app.root_path, 'uploads', 'books'), exist_ok=True)
    os.makedirs(os.path.join(app.root_path, 'uploads', 'covers'), exist_ok=True)
    
    # Загрузчик пользователей
    @app.login_manager.user_loader
    def load_user(user_id):
        try:
            cursor = app.mysql.connection.cursor()
            cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
            user_data = cursor.fetchone()
            if user_data:
                return User(
                    user_id=user_data['id'],
                    username=user_data['username'],
                    is_admin=bool(user_data['is_admin'])
                )
        except Exception:
            return None
        return None
    
    # Главная страница
    @app.route('/')
    def home():
        return redirect(url_for('books.library'))
    
    return app


if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)