from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for, current_app
from flask_login import login_required, current_user
from modules.database import get_db
import os
from werkzeug.utils import secure_filename
import MySQLdb
import logging

# Создаем blueprint для профилей
profile_bp = Blueprint('profile', __name__, url_prefix='/profile')

# Настройка логирования
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def allowed_file(filename):
    """Проверяет, является ли расширение файла допустимым"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif'}

@profile_bp.route('/', strict_slashes=False)
@login_required
def profile():
    """Отображает профиль пользователя"""
    try:
        db = get_db()
        cursor = db.cursor(MySQLdb.cursors.DictCursor)
        
        # Получаем информацию о пользователе
        cursor.execute("""
            SELECT u.*, 
                   COUNT(DISTINCT pr.book_id) as books_read,
                   COUNT(DISTINCT r.book_id) as books_rated,
                   AVG(r.rating) as average_rating
            FROM users u
            LEFT JOIN progress pr ON u.id = pr.user_id AND pr.progress = 100
            LEFT JOIN ratings r ON u.id = r.user_id
            WHERE u.id = %s
            GROUP BY u.id
        """, (current_user.id,))
        user = cursor.fetchone()
        if user and user['average_rating'] is None:
            user['average_rating'] = 0.0
        
        # Получаем последние прочитанные книги
        cursor.execute("""
            SELECT b.*, pr.progress, pr.last_read
            FROM books b
            JOIN progress pr ON b.id = pr.book_id
            WHERE pr.user_id = %s
            ORDER BY pr.last_read DESC
            LIMIT 5
        """, (current_user.id,))
        recent_books = cursor.fetchall()
        
        # Получаем последние оценки
        cursor.execute("""
            SELECT b.*, r.rating, r.review, r.created_at
            FROM books b
            JOIN ratings r ON b.id = r.book_id
            WHERE r.user_id = %s
            ORDER BY r.created_at DESC
            LIMIT 5
        """, (current_user.id,))
        recent_ratings = cursor.fetchall()
        
        # Получаем избранные книги
        cursor.execute("""
            SELECT b.*
            FROM books b
            JOIN favorites f ON b.id = f.book_id
            WHERE f.user_id = %s
            ORDER BY f.added_at DESC
            LIMIT 10
        """, (current_user.id,))
        favorite_books = cursor.fetchall()
        
        return render_template('profile.html',
                             user=user,
                             recent_books=recent_books,
                             recent_ratings=recent_ratings,
                             favorite_books=favorite_books)
                             
    except Exception as e:
        logger.error(f"Ошибка при загрузке профиля: {str(e)}")
        flash('Произошла ошибка при загрузке профиля', 'danger')
        return redirect(url_for('books.library'))

@profile_bp.route('/update', methods=['POST'])
@login_required
def update_profile():
    """Обновляет информацию профиля"""
    try:
        email = request.form.get('email')
        bio = request.form.get('bio')
        
        db = get_db()
        cursor = db.cursor()
        
        # Обновляем информацию
        cursor.execute("""
            UPDATE users 
            SET email = %s, bio = %s
            WHERE id = %s
        """, (email, bio, current_user.id))
        
        db.commit()
        flash('Профиль успешно обновлен', 'success')
        return redirect(url_for('profile.profile'))
        
    except Exception as e:
        logger.error(f"Ошибка при обновлении профиля: {str(e)}")
        flash('Произошла ошибка при обновлении профиля', 'danger')
        return redirect(url_for('profile.profile'))

@profile_bp.route('/upload_avatar', methods=['POST'])
@login_required
def upload_avatar():
    """Загружает аватар пользователя"""
    try:
        if 'avatar' not in request.files:
            return jsonify({'success': False, 'error': 'Файл не был отправлен'}), 400
            
        file = request.files['avatar']
        if file.filename == '':
            return jsonify({'success': False, 'error': 'Файл не был выбран'}), 400
            
        if not allowed_file(file.filename):
            return jsonify({'success': False, 'error': 'Недопустимый формат файла'}), 400
            
        # Сохраняем файл
        filename = secure_filename(f"avatar_{current_user.id}_{file.filename}")
        avatar_dir = os.path.join(current_app.root_path, 'static', 'avatars')
        os.makedirs(avatar_dir, exist_ok=True)
        file_path = os.path.join(avatar_dir, filename)
        file.save(file_path)
        
        # Обновляем путь к аватару в БД
        db = get_db()
        cursor = db.cursor()
        avatar_rel_path = f"avatars/{filename}"
        cursor.execute("""
            UPDATE users 
            SET avatar_path = %s
            WHERE id = %s
        """, (avatar_rel_path, current_user.id))
        db.commit()
        
        return jsonify({'success': True})
        
    except Exception as e:
        logger.error(f"Ошибка при загрузке аватара: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@profile_bp.route('/rate_book/<int:book_id>', methods=['POST'])
@login_required
def rate_book(book_id):
    """Оценивает книгу"""
    try:
        rating = int(request.form.get('rating', 0))
        review = request.form.get('review', '')
        
        if not 1 <= rating <= 5:
            return jsonify({'success': False, 'error': 'Недопустимая оценка'}), 400
            
        db = get_db()
        cursor = db.cursor()
        
        # Проверяем существование оценки
        cursor.execute("""
            SELECT id FROM ratings 
            WHERE user_id = %s AND book_id = %s
        """, (current_user.id, book_id))
        existing_rating = cursor.fetchone()
        
        if existing_rating:
            # Обновляем существующую оценку
            cursor.execute("""
                UPDATE ratings 
                SET rating = %s, review = %s
                WHERE user_id = %s AND book_id = %s
            """, (rating, review, current_user.id, book_id))
        else:
            # Добавляем новую оценку
            cursor.execute("""
                INSERT INTO ratings (user_id, book_id, rating, review)
                VALUES (%s, %s, %s, %s)
            """, (current_user.id, book_id, rating, review))
            
        # Обновляем средний рейтинг книги
        cursor.execute("""
            UPDATE books b
            SET average_rating = (
                SELECT AVG(rating) FROM ratings WHERE book_id = %s
            ),
            total_ratings = (
                SELECT COUNT(*) FROM ratings WHERE book_id = %s
            )
            WHERE id = %s
        """, (book_id, book_id, book_id))
        
        db.commit()
        return jsonify({'success': True})
        
    except Exception as e:
        logger.error(f"Ошибка при оценке книги: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500 