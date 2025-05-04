from flask import Blueprint, render_template, request, jsonify, send_file, flash, redirect, url_for
from flask_login import login_required, current_user
from modules.database import get_db
from modules.book_parser import BookParser
import os
import MySQLdb
from werkzeug.utils import secure_filename
from flask import current_app
import logging

books_bp = Blueprint('books', __name__)

# Настройка логирования
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Словарь переводов жанров
GENRE_TRANSLATIONS = {
    'sf_fantasy': 'Фэнтези',
    'sf': 'Научная фантастика',
    'detective': 'Детектив',
    'prose': 'Проза',
    'romance': 'Романтика',
    'adventure': 'Приключения',
    'science': 'Научная литература',
    'computers': 'Компьютерная литература',
    'children': 'Детская литература',
    'poetry': 'Поэзия',
    'religion': 'Религия',
    'thriller': 'Триллер',
    'horror': 'Ужасы',
    'history': 'История',
    'culture': 'Культура',
    'business': 'Бизнес',
    'fiction': 'Художественная литература',
    'nonfiction': 'Нехудожественная литература',
    None: 'Без жанра'
}

def allowed_file(filename):
    """Проверяет, является ли расширение файла допустимым"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'fb2', 'epub'}

@books_bp.route('/library')
@login_required
def library():
    try:
        db = get_db()
        cursor = db.cursor(MySQLdb.cursors.DictCursor)
        
        # Получаем все уникальные жанры
        cursor.execute("""
            SELECT DISTINCT genre 
            FROM books 
            WHERE genre IS NOT NULL 
            UNION 
            SELECT NULL as genre 
            FROM books 
            WHERE genre IS NULL
            ORDER BY COALESCE(genre, '')
        """)
        genres = [row['genre'] for row in cursor.fetchall()]
        
        # Получаем текущий жанр из параметров запроса
        current_genre = request.args.get('genre')
        
        # Формируем SQL запрос в зависимости от выбранного жанра
        if current_genre == 'None':
            cursor.execute("""
                SELECT b.*, 
                       COALESCE(pr.progress, 0) as progress
                FROM books b
                LEFT JOIN progress pr ON b.id = pr.book_id AND pr.user_id = %s
                WHERE b.genre IS NULL
                ORDER BY b.title
            """, (current_user.id,))
        elif current_genre:
            cursor.execute("""
                SELECT b.*, 
                       COALESCE(pr.progress, 0) as progress
                FROM books b
                LEFT JOIN progress pr ON b.id = pr.book_id AND pr.user_id = %s
                WHERE b.genre = %s
                ORDER BY b.title
            """, (current_user.id, current_genre))
        else:
            cursor.execute("""
                SELECT b.*, 
                       COALESCE(pr.progress, 0) as progress
                FROM books b
                LEFT JOIN progress pr ON b.id = pr.book_id AND pr.user_id = %s
                ORDER BY b.title
            """, (current_user.id,))
            
        books = cursor.fetchall()
        logger.debug(f"Получено книг из БД: {len(books)}")
        return render_template('library.html', 
                             books=books, 
                             genres=genres, 
                             current_genre=current_genre,
                             genre_translations=GENRE_TRANSLATIONS)
    except Exception as e:
        logger.error(f"Ошибка при получении списка книг: {str(e)}")
        flash('Произошла ошибка при загрузке библиотеки', 'danger')
        return render_template('library.html', 
                             books=[], 
                             genres=[], 
                             current_genre=None,
                             genre_translations=GENRE_TRANSLATIONS)

@books_bp.route('/read/<int:book_id>')
@login_required
def read_book(book_id):
    db = get_db()
    cursor = db.cursor(MySQLdb.cursors.DictCursor)
    
    # Получаем информацию о книге
    cursor.execute("""
        SELECT b.*, 
               COALESCE(pr.progress, 0) as progress
        FROM books b
        LEFT JOIN progress pr ON b.id = pr.book_id AND pr.user_id = %s
        WHERE b.id = %s
    """, (current_user.id, book_id))
    book = cursor.fetchone()
    
    if not book:
        flash('Книга не найдена')
        return redirect(url_for('books.library'))
    
    # Получаем содержимое книги
    book_path = os.path.join('uploads', 'books', book['file_path'])
    if not os.path.exists(book_path):
        flash('Файл книги не найден')
        return redirect(url_for('books.library'))
    
    parser = BookParser()
    content = parser.parse_book(book_path)
    
    # Вычисляем примерное количество страниц
    # (это приблизительная оценка, основанная на длине текста)
    total_pages = max(1, len(content.split('\n\n')) // 20)
    
    return render_template('reader.html', book=book, content=content, total_pages=total_pages)

@books_bp.route('/update_progress/<int:book_id>', methods=['POST'])
@login_required
def update_progress(book_id):
    try:
        progress = float(request.form.get('progress', 0))
        if not 0 <= progress <= 100:
            return jsonify({'error': 'Invalid progress value'}), 400
            
        db = get_db()
        cursor = db.cursor()
        
        # Проверяем существование записи
        cursor.execute("SELECT * FROM progress WHERE book_id = %s AND user_id = %s", 
                      (book_id, current_user.id))
        if cursor.fetchone():
            cursor.execute("""
                UPDATE progress 
                SET progress = %s 
                WHERE book_id = %s AND user_id = %s
            """, (progress, book_id, current_user.id))
        else:
            cursor.execute("""
                INSERT INTO progress (book_id, user_id, progress) 
                VALUES (%s, %s, %s)
            """, (book_id, current_user.id, progress))
            
        db.commit()
        return jsonify({'success': True})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@books_bp.route('/upload', methods=['POST'])
@login_required
def upload_book():
    if not current_user.is_admin:
        flash('У вас нет прав для загрузки книг', 'danger')
        return redirect(url_for('books.library'))
    if 'file' not in request.files:
        flash('Файл не был отправлен', 'danger')
        return redirect(url_for('books.library'))
    file = request.files['file']
    if file.filename == '':
        flash('Файл не был выбран', 'danger')
        return redirect(url_for('books.library'))
    if not allowed_file(file.filename):
        flash('Недопустимый формат файла. Поддерживаются только FB2 и EPUB', 'danger')
        return redirect(url_for('books.library'))
    try:
        # Проверяем размер файла
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)
        if file_size > current_app.config['MAX_CONTENT_LENGTH']:
            flash('Размер файла превышает допустимый лимит', 'danger')
            return redirect(url_for('books.library'))
        # Сохраняем файл книги
        filename = secure_filename(file.filename)
        book_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'books')
        os.makedirs(book_dir, exist_ok=True)
        file_path = os.path.join(book_dir, filename)
        file.save(file_path)
        logger.debug(f"Файл книги сохранён: {file_path}")
        # Парсим метаданные
        parser = BookParser()
        metadata = parser.parse_metadata(file_path)
        logger.debug(f"Получены метаданные: {metadata}")
        # Сохраняем обложку
        cover_path = None
        if metadata.get('cover'):
            cover_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'covers')
            os.makedirs(cover_dir, exist_ok=True)
            cover_filename = f"{os.path.splitext(filename)[0]}.jpg"
            cover_path = os.path.join('covers', cover_filename)
            parser.save_cover(metadata['cover'], os.path.join(current_app.config['UPLOAD_FOLDER'], cover_path))
        # Сохраняем информацию о книге в БД
        db = get_db()
        cursor = db.cursor()
        try:
            file_format = 'fb2' if filename.lower().endswith('.fb2') else 'epub'
            cursor.execute("""
                INSERT INTO books (title, author, genre, file_path, cover_path, file_format)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                metadata.get('title', 'Без названия'),
                metadata.get('author', 'Неизвестный автор'),
                metadata.get('genre'),
                filename,
                cover_path,
                file_format
            ))
            db.commit()
            logger.debug("Книга успешно сохранена в БД")
        except Exception as e:
            logger.error(f"Ошибка при сохранении в БД: {str(e)}")
            raise
        finally:
            cursor.close()
        flash('Книга успешно загружена', 'success')
        return jsonify({'success': True})
    except Exception as e:
        logger.error(f"Ошибка при загрузке книги: {str(e)}")
        flash(f'Ошибка при загрузке книги: {str(e)}', 'danger')
        # Удаляем файл, если он был сохранен
        if os.path.exists(file_path):
            os.remove(file_path)
        return jsonify({'success': False, 'error': str(e)})

@books_bp.route('/delete/<int:book_id>', methods=['POST'])
@login_required
def delete_book(book_id):
    if not current_user.is_admin:
        return jsonify({'success': False, 'error': 'Нет прав'}), 403
    try:
        db = get_db()
        cursor = db.cursor(MySQLdb.cursors.DictCursor)
        # Получаем информацию о книге
        cursor.execute('SELECT file_path, cover_path FROM books WHERE id = %s', (book_id,))
        book = cursor.fetchone()
        if not book:
            return jsonify({'success': False, 'error': 'Книга не найдена'}), 404
        # Удаляем запись о книге
        cursor.execute('DELETE FROM books WHERE id = %s', (book_id,))
        db.commit()
        # Удаляем файл книги
        if book['file_path']:
            book_file = os.path.join(current_app.config['UPLOAD_FOLDER'], 'books', book['file_path'])
            if os.path.exists(book_file):
                os.remove(book_file)
        # Удаляем обложку
        if book['cover_path']:
            cover_file = os.path.join(current_app.config['UPLOAD_FOLDER'], book['cover_path'])
            if os.path.exists(cover_file):
                os.remove(cover_file)
        return jsonify({'success': True})
    except Exception as e:
        logger.error(f"Ошибка при удалении книги: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})