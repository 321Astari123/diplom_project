from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for, current_app
from flask_login import login_required, current_user
from modules.database import get_db
import os
from werkzeug.utils import secure_filename
import MySQLdb
from extensions import bcrypt
import random
import string

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


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
        SELECT b.*, 
               COUNT(DISTINCT pr.user_id) as readers_count
        FROM books b
        LEFT JOIN progress pr ON b.id = pr.book_id
        GROUP BY b.id
        ORDER BY b.id DESC
        LIMIT 10
    """)
    recent_books = cursor.fetchall()
    
    return render_template('admin_panel.html', 
                         stats=stats,
                         recent_books=recent_books)


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
        return jsonify({'success': False, 'error': 'Нет доступа'}), 403
    db = get_db()
    cursor = db.cursor()
    # Генерируем новый пароль
    new_password = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
    password_hash = bcrypt.generate_password_hash(new_password).decode('utf-8')
    cursor.execute('UPDATE users SET password = %s WHERE id = %s', (password_hash, user_id))
    db.commit()
    return jsonify({'success': True, 'new_password': new_password})