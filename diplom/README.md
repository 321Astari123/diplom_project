# Онлайн библиотека

Веб-приложение для чтения книг в форматах FB2 и EPUB.

## Функциональность

- Регистрация и авторизация пользователей
- Загрузка книг в форматах FB2 и EPUB (для администраторов)
- Чтение книг онлайн
- Сохранение прогресса чтения
- Административная панель для управления книгами

## Технологии

- Python 3.8+
- Flask
- MySQL
- HTML/CSS/JavaScript
- Bootstrap 5

## Установка

1. Клонируйте репозиторий:
```bash
git clone https://github.com/yourusername/online-library.git
cd online-library
```

2. Создайте виртуальное окружение и активируйте его:
```bash
python -m venv venv
source venv/bin/activate  # для Linux/Mac
venv\Scripts\activate     # для Windows
```

3. Установите зависимости:
```bash
pip install -r requirements.txt
```

4. Создайте файл `.env` и настройте переменные окружения:
```
FLASK_APP=main.py
FLASK_ENV=development
SECRET_KEY=your-secret-key-here
MYSQL_HOST=localhost
MYSQL_USER=root
MYSQL_PASSWORD=your-mysql-password
MYSQL_DB=online_library
```

5. Создайте базу данных и таблицы:
```bash
mysql -u root -p < init_db.sql
```

6. Запустите приложение:
```bash
python main.py
```

## Структура проекта

```
online-library/
├── main.py              # Точка входа приложения
├── config.py            # Конфигурация приложения
├── requirements.txt     # Зависимости проекта
├── init_db.sql          # Скрипт инициализации БД
├── .env                 # Переменные окружения
├── modules/             # Модули приложения
│   ├── __init__.py
│   ├── auth.py         # Аутентификация
│   ├── books.py        # Управление книгами
│   ├── admin.py        # Административная панель
│   ├── models.py       # Модели данных
│   ├── database.py     # Работа с БД
│   └── book_parser.py  # Парсинг книг
├── templates/          # Шаблоны
│   ├── base.html
│   ├── login.html
│   ├── register.html
│   ├── library.html
│   ├── reader.html
│   └── admin_panel.html
└── uploads/           # Загруженные файлы
    ├── books/        # Книги
    └── covers/       # Обложки
```

## Тестовые аккаунты

- Администратор:
  - Email: admin@library.com
  - Пароль: admin123

- Пользователь:
  - Email: user123@example.com
  - Пароль: user123
