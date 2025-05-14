from app import app, db
from database import Book, User

with app.app_context():
    # Добавляем поля status и uploaded_by в существующие книги
    db.engine.execute('ALTER TABLE book ADD COLUMN status VARCHAR(20) DEFAULT "approved"')
    db.engine.execute('ALTER TABLE book ADD COLUMN uploaded_by INTEGER')
    
    # Устанавливаем uploaded_by для существующих книг (привязываем к первому админу)
    admin = User.query.filter_by(role='admin').first()
    if admin:
        db.engine.execute(f'UPDATE book SET uploaded_by = {admin.id} WHERE uploaded_by IS NULL')
    
    db.session.commit()
    print("Миграция выполнена успешно!") 