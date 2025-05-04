from flask_mysqldb import MySQL
import os

def init_db(app):
    """Инициализирует подключение к базе данных"""
    app.config['MYSQL_HOST'] = os.getenv('MYSQL_HOST', 'localhost')
    app.config['MYSQL_USER'] = os.getenv('MYSQL_USER', 'root')
    app.config['MYSQL_PASSWORD'] = os.getenv('MYSQL_PASSWORD', '')
    app.config['MYSQL_DB'] = os.getenv('MYSQL_DB', 'online_library')
    app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
    
    mysql = MySQL(app)
    return mysql

def get_db():
    """Возвращает подключение к базе данных"""
    from flask import current_app
    return current_app.mysql.connection