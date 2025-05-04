from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_bcrypt import generate_password_hash
from flask_login import login_user, logout_user, login_required, current_user
from extensions import bcrypt
from modules.models import User
from modules.database import get_db
import MySQLdb

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('books.library'))
        
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        if not email or not password:
            flash('Пожалуйста, заполните все поля')
            return redirect(url_for('auth.login'))

        db = get_db()
        cursor = db.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        user_data = cursor.fetchone()

        if user_data and bcrypt.check_password_hash(user_data['password_hash'], password):
            user = User(
                user_id=user_data['id'],
                username=user_data['username'],
                is_admin=bool(user_data['is_admin'])
            )
            login_user(user)
            flash('Вы успешно вошли в систему!')
            return redirect(url_for('books.library'))

        flash('Неверный email или пароль')
        return redirect(url_for('auth.login'))

    return render_template('login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('books.library'))

    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')

        if not all([username, email, password]):
            flash('Пожалуйста, заполните все поля')
            return redirect(url_for('auth.register'))

        db = get_db()
        cursor = db.cursor()

        # Проверка существующего пользователя
        cursor.execute("SELECT * FROM users WHERE email = %s OR username = %s", (email, username))
        if cursor.fetchone():
            flash('Email или имя пользователя уже существуют')
            return redirect(url_for('auth.register'))

        # Создание нового пользователя
        hashed_password = generate_password_hash(password)
        cursor.execute(
            "INSERT INTO users (username, email, password_hash, is_admin) VALUES (%s, %s, %s, %s)",
            (username, email, hashed_password, False)
        )
        db.commit()

        flash('Регистрация успешна! Пожалуйста, войдите.')
        return redirect(url_for('auth.login'))

    return render_template('register.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Вы вышли из системы')
    return redirect(url_for('auth.login'))