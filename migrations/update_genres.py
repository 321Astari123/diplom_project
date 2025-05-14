import os
import sys
import logging
import MySQLdb
from flask import Flask
from flask_mysqldb import MySQL

# Добавляем путь к корневой директории проекта
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Создаем экземпляр приложения Flask
app = Flask(__name__)
app.config.from_object('config')

# Инициализируем MySQL
mysql = MySQL(app)

# Настройка логирования
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Конфигурация базы данных
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'db': 'online_library'
}

def get_db_connection():
    """Создает подключение к базе данных"""
    return MySQLdb.connect(**DB_CONFIG)

def migrate():
    """Выполняет миграцию базы данных"""
    db = None
    cursor = None
    try:
        db = get_db_connection()
        cursor = db.cursor()
        
        # Проверяем существование таблицы books
        cursor.execute("SHOW TABLES LIKE 'books'")
        if not cursor.fetchone():
            logger.error("Таблица books не существует")
            return
            
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
        
        # Проверяем существование колонки genre
        cursor.execute("""
            SELECT COLUMN_NAME 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_NAME = 'books' AND COLUMN_NAME = 'genre'
        """)
        if cursor.fetchone():
            # Переносим существующие жанры в новую таблицу
            cursor.execute("""
                SELECT id, genre FROM books WHERE genre IS NOT NULL
            """)
            books = cursor.fetchall()
            
            for book_id, genre in books:
                if genre:
                    # Добавляем жанр
                    cursor.execute("""
                        INSERT IGNORE INTO genres (name)
                        VALUES (%s)
                    """, (genre,))
                    
                    # Получаем ID жанра
                    cursor.execute("""
                        SELECT id FROM genres WHERE name = %s
                    """, (genre,))
                    genre_id = cursor.fetchone()[0]
                    
                    # Создаем связь
                    cursor.execute("""
                        INSERT INTO book_genres (book_id, genre_id)
                        VALUES (%s, %s)
                    """, (book_id, genre_id))
            
            # Удаляем старую колонку genre из таблицы books
            cursor.execute("""
                ALTER TABLE books DROP COLUMN genre
            """)
        
        db.commit()
        logger.info("Миграция успешно выполнена")
        
    except Exception as e:
        logger.error(f"Ошибка при выполнении миграции: {str(e)}")
        if db:
            db.rollback()
        raise
    finally:
        if cursor:
            cursor.close()
        if db:
            db.close()

if __name__ == '__main__':
    migrate() 