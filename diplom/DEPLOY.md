# Инструкция по развертыванию

## Требования к серверу

- Ubuntu 20.04 LTS или новее
- Python 3.8+
- MySQL 8.0+
- Nginx
- Supervisor

## Установка зависимостей

1. Обновите систему:
```bash
sudo apt update
sudo apt upgrade -y
```

2. Установите необходимые пакеты:
```bash
sudo apt install -y python3-pip python3-venv nginx supervisor mysql-server
```

3. Настройте MySQL:
```bash
sudo mysql_secure_installation
```

4. Создайте базу данных и пользователя:
```bash
sudo mysql -u root -p
```
```sql
CREATE DATABASE online_library CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;
CREATE USER 'library_user'@'localhost' IDENTIFIED BY 'your-password';
GRANT ALL PRIVILEGES ON online_library.* TO 'library_user'@'localhost';
FLUSH PRIVILEGES;
```

## Настройка приложения

1. Создайте директорию для приложения:
```bash
sudo mkdir -p /var/www/online-library
sudo chown $USER:$USER /var/www/online-library
```

2. Клонируйте репозиторий:
```bash
cd /var/www/online-library
git clone https://github.com/yourusername/online-library.git .
```

3. Создайте виртуальное окружение:
```bash
python3 -m venv venv
source venv/bin/activate
```

4. Установите зависимости:
```bash
pip install -r requirements.txt
```

5. Создайте файл `.env`:
```bash
nano .env
```
```
FLASK_APP=main.py
FLASK_ENV=production
SECRET_KEY=your-secret-key-here
MYSQL_HOST=localhost
MYSQL_USER=library_user
MYSQL_PASSWORD=your-password
MYSQL_DB=online_library
```

6. Инициализируйте базу данных:
```bash
mysql -u library_user -p online_library < init_db.sql
```

## Настройка Gunicorn

1. Создайте файл конфигурации:
```bash
sudo nano /etc/supervisor/conf.d/online-library.conf
```
```ini
[program:online-library]
directory=/var/www/online-library
command=/var/www/online-library/venv/bin/gunicorn -w 3 -b 127.0.0.1:8000 main:app
user=www-data
autostart=true
autorestart=true
stderr_logfile=/var/log/online-library/err.log
stdout_logfile=/var/log/online-library/out.log
```

2. Создайте директорию для логов:
```bash
sudo mkdir -p /var/log/online-library
sudo chown www-data:www-data /var/log/online-library
```

3. Перезапустите Supervisor:
```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start online-library
```

## Настройка Nginx

1. Создайте файл конфигурации:
```bash
sudo nano /etc/nginx/sites-available/online-library
```
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static {
        alias /var/www/online-library/static;
    }

    location /uploads {
        alias /var/www/online-library/uploads;
    }
}
```

2. Активируйте конфигурацию:
```bash
sudo ln -s /etc/nginx/sites-available/online-library /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

## Настройка SSL (опционально)

1. Установите Certbot:
```bash
sudo apt install -y certbot python3-certbot-nginx
```

2. Получите сертификат:
```bash
sudo certbot --nginx -d your-domain.com
```

## Обновление приложения

1. Остановите приложение:
```bash
sudo supervisorctl stop online-library
```

2. Обновите код:
```bash
cd /var/www/online-library
git pull
```

3. Обновите зависимости:
```bash
source venv/bin/activate
pip install -r requirements.txt
```

4. Примените миграции базы данных (если есть):
```bash
mysql -u library_user -p online_library < migrations.sql
```

5. Запустите приложение:
```bash
sudo supervisorctl start online-library
```

## Мониторинг

1. Проверьте статус приложения:
```bash
sudo supervisorctl status online-library
```

2. Просмотрите логи:
```bash
sudo tail -f /var/log/online-library/err.log
sudo tail -f /var/log/online-library/out.log
```

## Безопасность

1. Настройте брандмауэр:
```bash
sudo ufw allow 80
sudo ufw allow 443
sudo ufw enable
```

2. Регулярно обновляйте систему и зависимости:
```bash
sudo apt update
sudo apt upgrade -y
source /var/www/online-library/venv/bin/activate
pip install -r requirements.txt --upgrade
```

3. Настройте резервное копирование базы данных:
```bash
sudo nano /etc/cron.daily/backup-database
```
```bash
#!/bin/bash
mysqldump -u library_user -p online_library > /var/backups/online-library-$(date +%Y%m%d).sql
gzip /var/backups/online-library-$(date +%Y%m%d).sql
find /var/backups -name "online-library-*.sql.gz" -mtime +7 -delete
```
```bash
sudo chmod +x /etc/cron.daily/backup-database
``` 