from flask import render_template, request, flash, redirect, url_for, abort
from flask_login import login_required, current_user
from app import books_bp
from database import Book
from app import db

@books_bp.route('/upload', methods=['GET', 'POST'])
@login_required
def upload_book():
    if request.method == 'POST':
        # Здесь должен быть ваш код обработки загрузки книги
        # Например, получение данных из формы, сохранение файла и создание записи в БД
        # Ниже пример структуры (дополните своим кодом):
        # title = request.form.get('title')
        # ...
        # db.session.add(book)
        # db.session.commit()
        # flash(...)
        return redirect(url_for('books.library'))
    return render_template('upload_book.html')

# Добавляем роут для модерации (только для админов)
@books_bp.route('/admin/moderate')
@login_required
def moderate_books():
    if current_user.role != 'admin':
        abort(403)
    
    pending_books = Book.query.filter_by(status='pending').all()
    return render_template('admin/moderate_books.html', books=pending_books)

@books_bp.route('/admin/moderate/<int:book_id>/<action>')
@login_required
def moderate_book(book_id, action):
    if current_user.role != 'admin':
        abort(403)
    
    book = Book.query.get_or_404(book_id)
    
    if action == 'approve':
        book.status = 'approved'
        flash(f'Книга "{book.title}" одобрена!', 'success')
    elif action == 'reject':
        book.status = 'rejected'
        flash(f'Книга "{book.title}" отклонена!', 'warning')
    
    db.session.commit()
    return redirect(url_for('books.moderate_books'))

@books_bp.route('/library')
def library():
    # Показываем только одобренные книги для обычных пользователей
    # Админы видят все книги
    if current_user.is_authenticated and current_user.role == 'admin':
        books = Book.query.all()
    else:
        books = Book.query.filter_by(status='approved').all()
    
    # ... existing code ...
# ... existing code ... 