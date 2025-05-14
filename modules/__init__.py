from flask import Blueprint

# Создаем blueprint'ы
profile_bp = Blueprint('profile', __name__, url_prefix='/profile')
books_bp = Blueprint('books', __name__, url_prefix='/books')
auth_bp = Blueprint('auth', __name__, url_prefix='/auth')
admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# Импортируем маршруты
from . import profile
from . import books
from . import auth
from . import admin

__all__ = ['profile_bp', 'books_bp', 'auth_bp', 'admin_bp']
