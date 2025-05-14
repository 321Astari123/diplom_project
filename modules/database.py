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
    app.mysql = mysql  # Сохраняем объект mysql в приложении
    
    # Создаем таблицы при инициализации
    create_tables(app)
    
    return mysql

def get_db():
    """Возвращает подключение к базе данных"""
    from flask import current_app
    return current_app.mysql.connection

def create_tables(app):
    """Создает необходимые таблицы в базе данных"""
    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        
        # Создаем таблицу пользователей
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(80) UNIQUE NOT NULL,
                password_hash VARCHAR(120) NOT NULL,
                is_admin BOOLEAN DEFAULT FALSE,
                email VARCHAR(120) UNIQUE,
                avatar_path VARCHAR(255),
                bio TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Создаем таблицу книг
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS books (
                id INT AUTO_INCREMENT PRIMARY KEY,
                title VARCHAR(255) NOT NULL,
                author VARCHAR(255),
                file_path VARCHAR(255) NOT NULL,
                cover_path VARCHAR(255),
                file_format VARCHAR(10) NOT NULL,
                average_rating FLOAT DEFAULT 0,
                total_ratings INT DEFAULT 0,
                added_by INT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_approved BOOLEAN DEFAULT FALSE,
                FOREIGN KEY (added_by) REFERENCES users(id) ON DELETE SET NULL
            )
        """)
        
        # Создаем таблицу рейтингов
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ratings (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                book_id INT NOT NULL,
                rating INT NOT NULL CHECK (rating BETWEEN 1 AND 5),
                review TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE KEY unique_user_book (user_id, book_id),
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE CASCADE
            )
        """)
        
        # Создаем таблицу жанров
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS genres (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) UNIQUE NOT NULL
            )
        """)
        
        # Создаем таблицу связи книг и жанров
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS book_genres (
                book_id INT,
                genre_id INT,
                PRIMARY KEY (book_id, genre_id),
                FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE CASCADE,
                FOREIGN KEY (genre_id) REFERENCES genres(id) ON DELETE CASCADE
            )
        """)
        
        # Создаем таблицу прогресса чтения
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS progress (
                user_id INT,
                book_id INT,
                progress FLOAT DEFAULT 0,
                last_read TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (user_id, book_id),
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE CASCADE
            )
        """)
        
        # Создаем таблицу для хранения сброшенных паролей
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS reset_passwords (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                password VARCHAR(255) NOT NULL,
                reset_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        ''')
        
        # Создаем таблицу для просмотров
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS views (
                id INT AUTO_INCREMENT PRIMARY KEY,
                book_id INT NOT NULL,
                user_id INT NOT NULL,
                viewed_at DATETIME NOT NULL,
                UNIQUE KEY unique_view (book_id, user_id),
                FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE CASCADE,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)
        
        # Создаем таблицу для избранного
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS favorites (
                id INT AUTO_INCREMENT PRIMARY KEY,
                book_id INT NOT NULL,
                user_id INT NOT NULL,
                added_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                UNIQUE KEY unique_favorite (book_id, user_id),
                FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE CASCADE,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)
        
        # Создаем таблицу для комментариев
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS comments (
                id INT AUTO_INCREMENT PRIMARY KEY,
                book_id INT NOT NULL,
                user_id INT NOT NULL,
                content TEXT NOT NULL,
                created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE CASCADE,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)
        
        db.commit()