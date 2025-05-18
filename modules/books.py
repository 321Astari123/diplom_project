from flask import Blueprint, render_template, request, jsonify, send_file, flash, redirect, url_for
from flask_login import login_required, current_user
from modules.database import get_db
from modules.book_parser import BookParser
import os
import MySQLdb
from werkzeug.utils import secure_filename
from flask import current_app
import logging
from modules.genres import GENRES as genre_translations
from datetime import datetime, timedelta

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

def beautify_genres(genres):
    return sorted([
        g.strip().capitalize() for g in set(genres) if g and g.strip()
    ])

@books_bp.route('/library')
@login_required
def library():
    try:
        db = get_db()
        cursor = db.cursor(MySQLdb.cursors.DictCursor)
        # Получаем все уникальные жанры
        cursor.execute("""
            SELECT DISTINCT g.name 
            FROM genres g
            ORDER BY g.name
        """)
        genres = [row['name'] for row in cursor.fetchall()]
        logger.debug(f"Получены жанры из БД: {genres}")
        # Получаем текущий жанр из параметров запроса
        current_genre = request.args.get('genre')
        # Формируем SQL запрос в зависимости от выбранного жанра
        if current_genre:
            if current_user.is_admin:
                cursor.execute("""
                    SELECT b.*, 
                           COALESCE(pr.progress, 0) as progress,
                           COALESCE(GROUP_CONCAT(DISTINCT g.name), '') as genres
                    FROM books b
                    LEFT JOIN progress pr ON b.id = pr.book_id AND pr.user_id = %s
                    LEFT JOIN book_genres bg ON b.id = bg.book_id
                    LEFT JOIN genres g ON bg.genre_id = g.id
                    WHERE g.name = %s
                    GROUP BY b.id
                    ORDER BY b.title
                """, (current_user.id, current_genre))
            else:
                cursor.execute("""
                    SELECT b.*, 
                           COALESCE(pr.progress, 0) as progress,
                           COALESCE(GROUP_CONCAT(DISTINCT g.name), '') as genres
                    FROM books b
                    LEFT JOIN progress pr ON b.id = pr.book_id AND pr.user_id = %s
                    LEFT JOIN book_genres bg ON b.id = bg.book_id
                    LEFT JOIN genres g ON bg.genre_id = g.id
                    WHERE g.name = %s AND b.is_approved = TRUE
                    GROUP BY b.id
                    ORDER BY b.title
                """, (current_user.id, current_genre))
        else:
            if current_user.is_admin:
                cursor.execute("""
                    SELECT b.*, 
                           COALESCE(pr.progress, 0) as progress,
                           COALESCE(GROUP_CONCAT(DISTINCT g.name), '') as genres
                    FROM books b
                    LEFT JOIN progress pr ON b.id = pr.book_id AND pr.user_id = %s
                    LEFT JOIN book_genres bg ON b.id = bg.book_id
                    LEFT JOIN genres g ON bg.genre_id = g.id
                    GROUP BY b.id
                    ORDER BY b.title
                """, (current_user.id,))
            else:
                cursor.execute("""
                    SELECT b.*, 
                           COALESCE(pr.progress, 0) as progress,
                           COALESCE(GROUP_CONCAT(DISTINCT g.name), '') as genres
                    FROM books b
                    LEFT JOIN progress pr ON b.id = pr.book_id AND pr.user_id = %s
                    LEFT JOIN book_genres bg ON b.id = bg.book_id
                    LEFT JOIN genres g ON bg.genre_id = g.id
                    WHERE b.is_approved = TRUE
                    GROUP BY b.id
                    ORDER BY b.title
                """, (current_user.id,))
        books = cursor.fetchall()
        logger.debug(f"Получены книги из БД: {books}")
        # Преобразуем строку жанров в список
        for book in books:
            book['genres'] = beautify_genres(book['genres'].split(',')) if book['genres'] else []
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
               COALESCE(pr.progress, 0) as progress,
               COALESCE(GROUP_CONCAT(DISTINCT g.name), '') as genres
        FROM books b
        LEFT JOIN progress pr ON b.id = pr.book_id AND pr.user_id = %s
        LEFT JOIN book_genres bg ON b.id = bg.book_id
        LEFT JOIN genres g ON bg.genre_id = g.id
        WHERE b.id = %s
        GROUP BY b.id
    """, (current_user.id, book_id))
    book = cursor.fetchone()
    
    logger.debug(f"Получена книга из БД: {book}")

    if not book:
        flash('Книга не найдена')
        return redirect(url_for('books.library'))
    
    # Преобразуем строку жанров в список
    book['genres'] = beautify_genres(book['genres'].split(',')) if book['genres'] else []
    
    # Получаем содержимое книги
    book_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'books', book['file_path'])
    if not os.path.exists(book_path):
        flash('Файл книги не найдена')
        return redirect(url_for('books.library'))
    
    parser = BookParser()
    metadata, content = parser.parse_book(book_path)
    logger.debug(f"Метаданные после парсинга: {metadata}")
    logger.debug(f"Жанры в объекте book до обновления: {book['genres']}")
    
    # Не перезаписываем автора и жанры!
    logger.debug(f"Жанры в объекте book после обновления: {book['genres']}")
    
    # Вычисляем примерное количество страниц
    # Используем более точный метод подсчета страниц
    paragraphs = content.split('\n\n')
    words_per_page = 250  # Примерное количество слов на странице
    total_words = sum(len(p.split()) for p in paragraphs)
    total_pages = max(1, total_words // words_per_page)
    
    # Вычисляем текущую страницу на основе прогресса
    current_page = 1
    if book['progress'] > 0:
        current_page = max(1, min(total_pages, round((book['progress'] / 100) * total_pages)))
    
    logger.debug(f"Вычислено страниц: {total_pages}, текущая страница: {current_page}")

    return render_template('reader.html',
                         book=book, 
                         content=content, 
                         total_pages=total_pages,
                         current_page=current_page,
                         genre_translations=genre_translations)

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

@books_bp.route('/upload', methods=['GET', 'POST'])
@login_required
def upload_book():
    db = get_db()
    cursor = db.cursor(MySQLdb.cursors.DictCursor)
    if request.method == 'POST':
        import time
        max_retries = 3
        for attempt in range(max_retries):
            try:
                # Проверка лимита для обычных пользователей
                if not current_user.is_admin:
                    today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
                    cursor.execute("SELECT COUNT(*) as count FROM books WHERE added_by = %s AND created_at >= %s", (current_user.id, today_start))
                    result = cursor.fetchone()

                    count_today = 0
                    if result and 'count' in result:
                        count_today = result['count']

                    if count_today >= 5:
                        flash('Вы можете загружать не более 5 книг в день. Попробуйте завтра.', 'warning')
                        return redirect(url_for('books.upload_book'))

                if 'file' not in request.files:
                    flash('Файл не был отправлен', 'danger')
                    return redirect(url_for('books.upload_book'))
                file = request.files['file']
                if file.filename == '':
                    flash('Файл не был выбран', 'danger')
                    return redirect(url_for('books.upload_book'))
                if not allowed_file(file.filename):
                    flash('Недопустимый формат файла. Поддерживаются только FB2 и EPUB', 'danger')
                    return redirect(url_for('books.upload_book'))

                # Проверяем размер файла
                file.seek(0, os.SEEK_END)
                file_size = file.tell()
                file.seek(0)
                if file_size > current_app.config.get('MAX_CONTENT_LENGTH', 20*1024*1024):
                    flash('Размер файла превышает допустимый лимит', 'danger')
                    return redirect(url_for('books.upload_book'))

                # Сохраняем файл книги
                filename = secure_filename(file.filename)
                book_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'books')
                os.makedirs(book_dir, exist_ok=True)
                file_path = os.path.join(book_dir, filename)
                file.save(file_path)
                logger.debug(f"Файл книги сохранён: {file_path}")

                # Парсим метаданные
                parser = BookParser()
                try:
                    metadata = parser.parse_metadata(file_path)
                    # --- ДОБАВЛЕНА ОЧЕНЬ БЛИЗКАЯ ЛОГ-СТРОКА ---
                    logger.debug("!!! Сразу после parser.parse_metadata. Метаданные получены.")
                    # -----------------------------------------
                    logger.debug(f"Получены метаданные: {metadata}")
                    # --- Добавлено для отладки KeyError: 0 ---
                    logger.debug(f"Тип метаданных: {type(metadata)}")
                    if isinstance(metadata, dict):
                        logger.debug(f"Ключи в метаданных: {metadata.keys()}")
                        if 'genres' in metadata:
                             logger.debug(f"Тип metadata['genres']: {type(metadata['genres'])}")
                             logger.debug(f"Содержимое metadata['genres']: {metadata['genres']}")
                    # ---------------------------------------
                except Exception as parser_error:
                    # Если парсинг не удался, логируем ошибку и возвращаем сообщение пользователю
                    logger.error(f"Ошибка парсинга метаданных книги {filename}: {str(parser_error)}")
                    # Удаляем сохраненный файл книги, так как он не был успешно обработан
                    if os.path.exists(file_path):
                        os.remove(file_path)
                    flash(f'Ошибка при обработке файла книги: {str(parser_error)}', 'danger')
                    return redirect(url_for('books.upload_book'))

                # Сохраняем обложку
                cover_path = None
                book_cover_data = metadata.get('cover') # Получаем данные обложки
                
                # --- Добавлено для устойчивости и отладки ---
                # Проверяем, что данные обложки не None и имеют ожидаемый формат перед использованием
                # BookParser, вероятно, возвращает бинарные данные или путь, но точно не число 0, список или словарь, которые вызвали бы KeyError:0
                if book_cover_data and not isinstance(book_cover_data, (int, float, list, tuple, dict)): # Добавляем проверки на неожидаемые типы, особенно число 0
                # ---------------------------------------
                    try:
                        cover_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'covers')
                        os.makedirs(cover_dir, exist_ok=True)
                        cover_filename = f"{os.path.splitext(filename)[0]}.jpg"
                        cover_path = os.path.join('covers', cover_filename)
                        parser.save_cover(book_cover_data, os.path.join(current_app.config['UPLOAD_FOLDER'], cover_path))
                    except Exception as cover_save_error:
                        logger.error(f"Ошибка при сохранении обложки для книги {filename}: {str(cover_save_error)}")
                        # Продолжаем без обложки, не прерывая загрузку книги
                        cover_path = None # Сбрасываем cover_path на None при ошибке сохранения

                # --- Дополнительное детальное логирование перед использованием метаданных ---
                logger.debug(f"Проверка 'cover': {metadata.get('cover')}") # Перед доступом metadata.get('cover')
                # Перед обработкой обложки. (логирование уже добавлено)
                # ... код сохранения обложки ...

                # Перед сохранением в БД
                file_format = 'fb2' if filename.lower().endswith('.fb2') else 'epub'
                author = metadata.get('author')
                if not author or not isinstance(author, str) or not author.strip():
                    author = 'Неизвестный автор'
                is_approved = True if current_user.is_admin else False
                now = datetime.now()

                logger.debug(f"Проверка 'title': {metadata.get('title')}") # Перед доступом metadata.get('title')
                logger.debug(f"Проверка 'author': {author}") # Перед использованием author (уже обработан)
                logger.debug(f"Проверка 'filename': {filename}") # Перед использованием filename
                logger.debug(f"Проверка 'cover_path': {cover_path}") # Перед использованием cover_path
                logger.debug(f"Проверка 'file_format': {file_format}") # Перед использованием file_format
                logger.debug(f"Проверка 'publication_year': {metadata.get('publication_year')}") # Перед доступом metadata.get('publication_year')
                logger.debug(f"Проверка 'isbn': {metadata.get('isbn')}") # Перед доступом metadata.get('isbn')
                logger.debug(f"Проверка 'language': {metadata.get('language')}") # Перед доступом metadata.get('language')
                logger.debug(f"Проверка 'pages': {metadata.get('pages')}") # Перед доступом metadata.get('pages')
                logger.debug(f"Проверка 'added_by': {current_user.id}")
                logger.debug(f"Проверка 'is_approved': {is_approved}")
                logger.debug(f"Проверка 'now': {now}")

                # Сохраняем информацию о книге в БД
                cursor.execute("""
                    INSERT INTO books (title, author, file_path, cover_path, file_format, publication_year, isbn, language, pages, added_by, is_approved, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    metadata.get('title', 'Без названия'),
                    author,
                    filename,
                    cover_path,
                    file_format,
                    metadata.get('publication_year'),
                    metadata.get('isbn'),
                    metadata.get('language'),
                    metadata.get('pages'),
                    current_user.id,
                    is_approved,
                    now
                ))
                book_id = cursor.lastrowid

                # Перед обработкой жанров
                logger.debug(f"Проверка 'genres' перед обработкой: {metadata.get('genres')}") # Перед доступом metadata.get('genres')
                # Сохраняем жанры
                genres = metadata.get('genres', []) # Получаем список жанров
                
                # --- Добавлено для отладки и устойчивости ---
                # Проверяем, что genres является списком или кортежем перед итерацией
                if not isinstance(genres, (list, tuple)):
                    logger.error(f"Неожиданный тип genres: {type(genres)}, ожидается список или кортеж.")
                    genres = [] # Заменяем на пустой список, чтобы избежать ошибки в цикле
                # ---------------------------------------

                if genres: # Если список жанров (теперь гарантированно) не пустой
                    used_genre_ids = set()
                    for genre_name in genres:
                        # Убедимся, что genre_name не None и не пустая строка
                        if not genre_name or not genre_name.strip():
                            continue
                        
                        # Ищем или создаем жанр
                        cursor.execute("""
                            INSERT IGNORE INTO genres (name)
                            VALUES (%s)
                        """, (genre_name.strip(),)) # Используем strip() на всякий случай

                        cursor.execute("""
                            SELECT id FROM genres WHERE name = %s
                        """, (genre_name.strip(),)) # И здесь тоже

                        genre_row = cursor.fetchone()

                        # --- Добавлено для отладки KeyError: 0 в жанрах ---
                        logger.debug(f"Результат fetchone() для жанра '{genre_name.strip()}': {genre_row}")
                        logger.debug(f"Тип fetchone() для жанра '{genre_name.strip()}': {type(genre_row)}")
                        # -------------------------------------------------

                        genre_id = None
                        # Явно проверяем, что genre_row не None и что 'id' есть в словаре
                        if genre_row is not None and 'id' in genre_row:
                             genre_id = genre_row['id']
                        # Если genre_row is None или нет ключа 'id', genre_id останется None

                        if genre_id is not None and genre_id not in used_genre_ids:
                            try:
                                cursor.execute("""
                                    INSERT INTO book_genres (book_id, genre_id)
                                    VALUES (%s, %s)
                                """, (book_id, genre_id))
                                used_genre_ids.add(genre_id)
                            except MySQLdb.IntegrityError:
                                # Пропускаем, если связь книга-жанр уже существует
                                logger.warning(f"Связь для книги {book_id} и жанра {genre_id} уже существует.")
                                pass # Пропускаем, если такая связь уже есть
                            except Exception as e:
                                logger.error(f"Ошибка при связывании книги {book_id} с жанром {genre_id}: {str(e)}")
                db.commit()
                logger.debug("Книга успешно сохранена в БД")

                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return jsonify({'success': True, 'message': 'Книга успешно загружена!'}), 200
                if is_approved:
                    flash('Книга успешно загружена!', 'success')
                else:
                    flash('Книга успешно загружена и направлена на модерацию!', 'info')
                return redirect(url_for('books.library'))
            except MySQLdb.OperationalError as e:
                if e.args[0] == 1213:  # Deadlock
                    logger.warning(f"Deadlock detected, attempt {attempt+1} of {max_retries}")
                    db.rollback()
                    time.sleep(0.5)
                    if attempt == max_retries - 1:
                        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                            return jsonify({'success': False, 'error': 'Deadlock, попробуйте ещё раз'}), 400
                        flash('Ошибка при загрузке книги: Deadlock, попробуйте ещё раз', 'danger')
                        return redirect(url_for('books.upload_book'))
                    continue
                else:
                    db.rollback()
                    logger.error(f"Ошибка при загрузке книги: {str(e)}")
                    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                        return jsonify({'success': False, 'error': str(e)}), 400
                    flash(f'Ошибка при загрузке книги: {str(e)}', 'danger')
                    return redirect(url_for('books.upload_book'))
            except Exception as e:
                db.rollback()
                logger.error(f"Ошибка при загрузке книги: Тип ошибки: {type(e).__name__}, Подробности: {e.args}")
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return jsonify({'success': False, 'error': str(e)}), 400
                flash(f'Ошибка при загрузке книги: {str(e)}', 'danger')
                return redirect(url_for('books.upload_book'))
    # GET-запрос — возвращаем форму загрузки
    return render_template('upload_book.html')

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

@books_bp.route('/details/<int:book_id>')
@login_required
def book_details(book_id):
    try:
        db = get_db()
        cursor = db.cursor(MySQLdb.cursors.DictCursor)
        
        # Получаем подробную информацию о книге
        cursor.execute("""
            SELECT b.*, 
                   COALESCE(GROUP_CONCAT(DISTINCT g.name), '') as genres,
                   COALESCE(pr.progress, 0) as progress,
                   COUNT(DISTINCT r.id) as total_ratings,
                   AVG(r.rating) as average_rating,
                   COUNT(DISTINCT v.id) as views,
                   COUNT(DISTINCT f.id) as favorites,
                   COUNT(DISTINCT c.id) as comments
            FROM books b
            LEFT JOIN book_genres bg ON b.id = bg.book_id
            LEFT JOIN genres g ON bg.genre_id = g.id
            LEFT JOIN progress pr ON b.id = pr.book_id AND pr.user_id = %s
            LEFT JOIN ratings r ON b.id = r.book_id
            LEFT JOIN views v ON b.id = v.book_id
            LEFT JOIN favorites f ON b.id = f.book_id
            LEFT JOIN comments c ON b.id = c.book_id
            WHERE b.id = %s
            GROUP BY b.id
        """, (current_user.id, book_id))
        
        book = cursor.fetchone()
        if not book:
            flash('Книга не найдена')
            return redirect(url_for('books.library'))
            
        # Преобразуем строку жанров в список
        book['genres'] = beautify_genres(book['genres'].split(',')) if book['genres'] else []
        
        # Увеличиваем счетчик просмотров
        cursor.execute("""
            INSERT INTO views (book_id, user_id, viewed_at)
            VALUES (%s, %s, NOW())
            ON DUPLICATE KEY UPDATE viewed_at = NOW()
        """, (book_id, current_user.id))
        db.commit()
        
        user_rating = None
        user_review = None
        if current_user.is_authenticated:
            cursor.execute(
                "SELECT rating, review FROM ratings WHERE user_id = %s AND book_id = %s",
                (current_user.id, book_id)
            )
            row = cursor.fetchone()
            if row:
                user_rating = row['rating']
                user_review = row['review']
        
        return render_template('book_details.html', 
                             book=book,
                             genre_translations=GENRE_TRANSLATIONS,
                             user_rating=user_rating,
                             user_review=user_review)
                             
    except Exception as e:
        logger.error(f"Ошибка при загрузке деталей книги: {str(e)}")
        flash('Произошла ошибка при загрузке информации о книге', 'danger')
        return redirect(url_for('books.library'))

@books_bp.route('/delete_bulk', methods=['POST'])
@login_required
def delete_bulk():
    if not current_user.is_admin:
        return jsonify({'success': False, 'error': 'Нет прав'}), 403
    try:
        ids = request.json.get('ids', [])
        if not ids:
            return jsonify({'success': False, 'error': 'Нет выбранных книг'}), 400
        db = get_db()
        cursor = db.cursor(MySQLdb.cursors.DictCursor)
        # Получаем пути файлов для удаления
        format_strings = ','.join(['%s'] * len(ids))
        cursor.execute(f'SELECT file_path, cover_path FROM books WHERE id IN ({format_strings})', tuple(ids))
        books = cursor.fetchall()
        # Удаляем записи
        cursor.execute(f'DELETE FROM books WHERE id IN ({format_strings})', tuple(ids))
        db.commit()
        # Удаляем файлы
        for book in books:
            if book['file_path']:
                book_file = os.path.join(current_app.config['UPLOAD_FOLDER'], 'books', book['file_path'])
                if os.path.exists(book_file):
                    os.remove(book_file)
            if book['cover_path']:
                cover_file = os.path.join(current_app.config['UPLOAD_FOLDER'], book['cover_path'])
                if os.path.exists(cover_file):
                    os.remove(cover_file)
        return jsonify({'success': True})
    except Exception as e:
        logger.error(f"Ошибка при массовом удалении книг: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})

@books_bp.route('/read/<int:book_id>/page/<int:page>')
@login_required
def get_page(book_id, page):
    """Возвращает содержимое страницы для AJAX-запроса"""
    try:
        db = get_db()
        cursor = db.cursor(MySQLdb.cursors.DictCursor)
        
        # Получаем информацию о книге
        cursor.execute('SELECT * FROM books WHERE id = %s', (book_id,))
        book = cursor.fetchone()
        
        if not book:
            return 'Книга не найдена', 404
            
        # Получаем содержимое страницы
        content = get_page_content(book, page)
        
        # Если это AJAX-запрос, возвращаем только содержимое
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return content
            
        # Иначе возвращаем полную страницу
        return render_template('read_book.html',
                             book=book,
                             content=content,
                             current_page=page,
                             total_pages=get_total_pages(book))
                             
    except Exception as e:
        logger.error(f"Ошибка при чтении страницы: {str(e)}")
        return str(e), 500

@books_bp.route('/favorite/<int:book_id>', methods=['POST'])
@login_required
def add_favorite(book_id):
    db = get_db()
    cursor = db.cursor()
    try:
        cursor.execute("""
            INSERT IGNORE INTO favorites (book_id, user_id, added_at)
            VALUES (%s, %s, NOW())
        """, (book_id, current_user.id))
        db.commit()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@books_bp.route('/unfavorite/<int:book_id>', methods=['POST'])
@login_required
def remove_favorite(book_id):
    db = get_db()
    cursor = db.cursor()
    try:
        cursor.execute("""
            DELETE FROM favorites WHERE book_id = %s AND user_id = %s
        """, (book_id, current_user.id))
        db.commit()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@books_bp.route('/is_favorite/<int:book_id>', methods=['GET'])
@login_required
def is_favorite(book_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("""
        SELECT 1 FROM favorites WHERE book_id = %s AND user_id = %s
    """, (book_id, current_user.id))
    result = cursor.fetchone()
    return jsonify({'is_favorite': bool(result)})

@books_bp.route('/moderate')
@login_required
def moderate_books():
    if not current_user.is_admin:
        flash('Нет доступа', 'danger')
        return redirect(url_for('books.library'))
    db = get_db()
    cursor = db.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("""
        SELECT b.*, u.username as added_by_username
        FROM books b
        LEFT JOIN users u ON b.added_by = u.id
        WHERE b.is_approved = FALSE
        ORDER BY b.id DESC
    """)
    books = cursor.fetchall()
    return render_template('admin/moderate_books.html', books=books)

@books_bp.route('/moderate/<int:book_id>/<action>')
@login_required
def moderate_book(book_id, action):
    if not current_user.is_admin:
        flash('Нет доступа', 'danger')
        return redirect(url_for('books.library'))
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT * FROM books WHERE id = %s', (book_id,))
    book = cursor.fetchone()
    if not book:
        flash('Книга не найдена', 'danger')
        return redirect(url_for('books.moderate_books'))
    if action == 'approve':
        cursor.execute('UPDATE books SET is_approved = TRUE WHERE id = %s', (book_id,))
        flash('Книга одобрена!', 'success')
    elif action == 'reject':
        cursor.execute('DELETE FROM books WHERE id = %s', (book_id,))
        flash('Книга отклонена и удалена!', 'warning')
    db.commit()
    return redirect(url_for('books.moderate_books'))