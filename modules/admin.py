from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for, current_app
from flask_login import login_required, current_user
from modules.database import get_db
import os
from werkzeug.utils import secure_filename
import MySQLdb
from extensions import bcrypt
import random
import string
from werkzeug.security import generate_password_hash
import logging
from functools import wraps
from modules.book_parser import BookParser

# Настройка логирования
logger = logging.getLogger(__name__)

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('У вас нет прав доступа к административной панели', 'danger')
            return redirect(url_for('books.library'))
        return f(*args, **kwargs)
    return decorated_function


def init_admin(app):
    app.config['UPLOAD_FOLDER'] = os.path.join('static', 'books')
    app.config['COVER_FOLDER'] = os.path.join('static', 'covers')
    app.config['ALLOWED_EXTENSIONS'] = {'txt', 'pdf', 'epub'}
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['COVER_FOLDER'], exist_ok=True)


@admin_bp.before_request
def check_admin():
    if not current_user.is_authenticated or not current_user.is_admin:
        flash('У вас нет прав доступа к административной панели')
        return redirect(url_for('books.library'))


@admin_bp.route('/')
@login_required
def admin_panel():
    db = get_db()
    cursor = db.cursor(MySQLdb.cursors.DictCursor)

    # Получаем статистику
    cursor.execute("SELECT COUNT(*) as total_books FROM books")
    stats = cursor.fetchone()

    # Получаем последние добавленные книги
    cursor.execute("""
        SELECT b.*, u.username as added_by_username
        FROM books b
        LEFT JOIN users u ON b.added_by = u.id
        ORDER BY b.id DESC
        LIMIT 10
    """)
    recent_books = cursor.fetchall()

    # Получаем книги на модерации
    cursor.execute("""
        SELECT b.*, u.username as added_by_username
        FROM books b
        LEFT JOIN users u ON b.added_by = u.id
        WHERE b.is_approved = FALSE
        ORDER BY b.id DESC
    """)
    pending_books = cursor.fetchall()

    return render_template('admin_panel.html',
                           stats=stats,
                           recent_books=recent_books,
                           pending_books=pending_books)


@admin_bp.route('/delete_book/<int:book_id>', methods=['POST'])
@login_required
def delete_book(book_id):
    try:
        db = get_db()
        cursor = db.cursor()
        
        # Получаем информацию о книге
        cursor.execute("SELECT file_path, cover_path FROM books WHERE id = %s", (book_id,))
        book = cursor.fetchone()
        
        if not book:
            flash('Книга не найдена')
            return redirect(url_for('admin.admin_panel'))
            
        # Удаляем файлы
        if book['file_path']:
            file_path = os.path.join('uploads', 'books', book['file_path'])
            if os.path.exists(file_path):
                os.remove(file_path)
                
        if book['cover_path']:
            cover_path = os.path.join('uploads', 'covers', book['cover_path'])
            if os.path.exists(cover_path):
                os.remove(cover_path)
                
        # Удаляем записи из БД
        cursor.execute("DELETE FROM progress WHERE book_id = %s", (book_id,))
        cursor.execute("DELETE FROM books WHERE id = %s", (book_id,))
        db.commit()
        
        flash('Книга успешно удалена')
        return redirect(url_for('admin.admin_panel'))
        
    except Exception as e:
        flash(f'Ошибка при удалении книги: {str(e)}')
        return redirect(url_for('admin.admin_panel'))


@admin_bp.route('/users')
@login_required
def users():
    if not current_user.is_admin:
        flash('Нет доступа', 'danger')
        return redirect(url_for('books.library'))
    db = get_db()
    cursor = db.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT id, username, email, is_admin FROM users')
    users = cursor.fetchall()
    return render_template('admin_users.html', users=users)


@admin_bp.route('/reset_password/<int:user_id>', methods=['POST'])
@login_required
def reset_password(user_id):
    if not current_user.is_admin:
        return jsonify({'success': False, 'error': 'Нет прав'}), 403
        
    try:
        # Генерируем случайный пароль
        new_password = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
        password_hash = generate_password_hash(new_password)
        
        db = get_db()
        cursor = db.cursor()
        
        # Обновляем пароль пользователя
        cursor.execute('UPDATE users SET password_hash = %s WHERE id = %s', (password_hash, user_id))
        
        # Сохраняем сброшенный пароль в истории
        cursor.execute('INSERT INTO reset_passwords (user_id, password) VALUES (%s, %s)', 
                      (user_id, new_password))
        
        db.commit()
        
        return jsonify({
            'success': True,
            'new_password': new_password
        })
    except Exception as e:
        logger.error(f"Ошибка при сбросе пароля: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@admin_bp.route('/reset_passwords_history')
@login_required
def reset_passwords_history():
    if not current_user.is_admin:
        flash('Нет доступа', 'danger')
        return redirect(url_for('books.library'))
    
    db = get_db()
    cursor = db.cursor(MySQLdb.cursors.DictCursor)
    
    # Получаем только последний сброшенный пароль для каждого пользователя
    cursor.execute('''
        SELECT rp.*, u.username
        FROM reset_passwords rp
        JOIN users u ON rp.user_id = u.id
        INNER JOIN (
            SELECT user_id, MAX(reset_date) as max_date
            FROM reset_passwords
            GROUP BY user_id
        ) last ON rp.user_id = last.user_id AND rp.reset_date = last.max_date
        ORDER BY rp.reset_date DESC
    ''')
    history = cursor.fetchall()
    
    return render_template('admin_reset_passwords.html', history=history)


@admin_bp.route('/book/<int:book_id>', methods=['GET'])
@login_required
@admin_required
def get_book(book_id):
    """Получает информацию о книге для редактирования"""
    try:
        db = get_db()
        cursor = db.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("""
            SELECT b.*, GROUP_CONCAT(DISTINCT g.name) as genres
            FROM books b
            LEFT JOIN book_genres bg ON b.id = bg.book_id
            LEFT JOIN genres g ON bg.genre_id = g.id
            WHERE b.id = %s
            GROUP BY b.id
        """, (book_id,))
        book = cursor.fetchone()
        if not book:
            return jsonify({'error': 'Книга не найдена'}), 404
        # Преобразуем жанры в список и убираем пустые
        book['genres'] = [g.strip() for g in (book['genres'] or '').split(',') if g.strip()]
        # Новые метаданные: publication_year, isbn, language, pages
        for field in ['publication_year', 'isbn', 'language', 'pages']:
            if book.get(field) is None:
                book[field] = ''
        return jsonify(book)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/book/<int:book_id>', methods=['POST'])
@login_required
@admin_required
def update_book_with_cover(book_id):
    """Обновляет информацию о книге, поддерживает загрузку новой обложки"""
    try:
        db = get_db()
        cursor = db.cursor()
        title = request.form.get('editTitle') or request.form.get('title')
        author = request.form.get('editAuthor') or request.form.get('author')
        genres = request.form.getlist('genres')
        # Обработка обложки
        cover_file = request.files.get('cover')
        cover_path = None
        if cover_file and cover_file.filename:
            filename = secure_filename(cover_file.filename)
            ext = os.path.splitext(filename)[1].lower()
            if ext not in ['.jpg', '.jpeg', '.png']:
                return jsonify({'success': False, 'error': 'Допустимы только JPG и PNG'}), 400
            cover_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'covers')
            os.makedirs(cover_dir, exist_ok=True)
            cover_filename = f"book_{book_id}{ext}"
            full_cover_path = os.path.join(cover_dir, cover_filename)
            cover_file.save(full_cover_path)
            cover_path = os.path.join('covers', cover_filename)
            # Обновляем путь к обложке
            cursor.execute("UPDATE books SET cover_path=%s WHERE id=%s", (cover_path, book_id))
        # Обновляем основную информацию о книге
        cursor.execute("""
            UPDATE books SET title=%s, author=%s WHERE id=%s
        """, (title, author, book_id))
        # Обновляем жанры
        cursor.execute("DELETE FROM book_genres WHERE book_id = %s", (book_id,))
        for genre in genres:
            cursor.execute("INSERT IGNORE INTO genres (name) VALUES (%s)", (genre,))
            cursor.execute("SELECT id FROM genres WHERE name = %s", (genre,))
            genre_id = cursor.fetchone()[0]
            cursor.execute("INSERT INTO book_genres (book_id, genre_id) VALUES (%s, %s)", (book_id, genre_id))
        db.commit()
        return jsonify({'success': True})
    except Exception as e:
        logger.error(f"Ошибка при обновлении книги: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@admin_bp.route('/fix_old_books', methods=['POST'])
@login_required
@admin_required
def fix_old_books():
    """Массово обновляет метаданные старых книг с пустыми полями publication_year, isbn, language, pages"""
    db = get_db()
    cursor = db.cursor(MySQLdb.cursors.DictCursor)
    parser = BookParser()
    updated = 0
    cursor.execute("""
        SELECT * FROM books
        WHERE publication_year IS NULL OR isbn IS NULL OR language IS NULL OR pages IS NULL
    """)
    books = cursor.fetchall()
    for book in books:
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'books', book['file_path'])
        if not os.path.exists(file_path):
            continue
        try:
            metadata = parser.parse_metadata(file_path)
            cursor.execute("""
                UPDATE books SET publication_year=%s, isbn=%s, language=%s, pages=%s WHERE id=%s
            """, (
                metadata.get('publication_year'),
                metadata.get('isbn'),
                metadata.get('language'),
                metadata.get('pages'),
                book['id']
            ))
            updated += 1
        except Exception as e:
            logger.error(f"Не удалось обновить книгу id={book['id']}: {e}")
            continue
    db.commit()
    flash(f'Обновлено книг: {updated}', 'success')
    return redirect(url_for('admin.admin_panel'))


@admin_bp.route('/delete_user/<int:user_id>', methods=['POST'])
@login_required
def delete_user(user_id):
    if not current_user.is_admin:
        return jsonify({'success': False, 'error': 'Нет прав'}), 403
    if current_user.id == user_id:
        return jsonify({'success': False, 'error': 'Нельзя удалить самого себя'}), 400
    try:
        db = get_db()
        cursor = db.cursor()
        # Удаляем связанные данные (прогресс, отзывы и т.д. если есть)
        cursor.execute('DELETE FROM progress WHERE user_id = %s', (user_id,))
        cursor.execute('DELETE FROM ratings WHERE user_id = %s', (user_id,))
        cursor.execute('DELETE FROM reset_passwords WHERE user_id = %s', (user_id,))
        # Удаляем пользователя
        cursor.execute('DELETE FROM users WHERE id = %s', (user_id,))
        db.commit()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@admin_bp.route('/make_admin/<int:user_id>', methods=['POST'])
@login_required
def make_admin(user_id):
    if not current_user.is_admin:
        return jsonify({'success': False, 'error': 'Нет прав'}), 403
    if current_user.id == user_id:
        return jsonify({'success': False, 'error': 'Нельзя назначить самого себя'}), 400
    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute('UPDATE users SET is_admin = TRUE WHERE id = %s', (user_id,))
        db.commit()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@admin_bp.route('/approve_book/<int:book_id>', methods=['POST'])
@login_required
def approve_book(book_id):
    if not current_user.is_admin:
        return jsonify({'success': False, 'error': 'Нет прав'}), 403
    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute('UPDATE books SET is_approved = TRUE WHERE id = %s', (book_id,))
        db.commit()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})