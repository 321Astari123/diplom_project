# Онлайн библиотека (Дипломный проект)

Веб-приложение для чтения книг в форматах FB2 и EPUB.

## Функциональность

- Регистрация и авторизация пользователей
- Загрузка книг в форматах FB2 и EPUB (для администраторов)
- Чтение книг онлайн с прогрессом
- Сохранение прогресса чтения
- Фильтрация и поиск по жанрам
- Административная панель для управления книгами и жанрами
- Модерация загружаемых книг

## Технологии

- Python 3.8+
- Flask
- MySQL
- HTML/CSS/JavaScript
- Bootstrap 5

## Быстрый старт (локально)

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

4. Создайте файл `.env` или скопируйте `.env.example`:
```
FLASK_APP=main.py
FLASK_ENV=development
SECRET_KEY=your-secret-key-here
MYSQL_HOST=localhost
MYSQL_USER=root
MYSQL_PASSWORD=your-mysql-password
MYSQL_DB=online_library
UPLOAD_FOLDER=static/uploads
MAX_CONTENT_LENGTH=20971520
```

5. Создайте базу данных и таблицы:
```bash
mysql -u root -p < init_db.sql
```

6. Запустите приложение:
```bash
python main.py
```


## Тестовые аккаунты

- **Администратор:**
  - Email: admin@library.com
  - Пароль: admin123

- **Пользователь:**
  - Надо пройти процедуру регистрации

## Особенности
- Для загрузки книг требуется роль администратора
- Поддерживаются только FB2 и EPUB
- Ограничение на размер файла: 20 МБ (можно изменить в .env)
- Прогресс чтения сохраняется для каждого пользователя

## Для преподавателя
- Для запуска требуется MySQL и Python 3.8+
- Все зависимости указаны в requirements.txt
- Структура БД — в maindb.sql
- Пример переменных окружения — в .env.example
