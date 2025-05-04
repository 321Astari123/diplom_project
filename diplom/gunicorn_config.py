import multiprocessing

# Количество воркеров
workers = multiprocessing.cpu_count() * 2 + 1

# Путь к приложению
wsgi_app = "wsgi:app"

# Путь к логам
accesslog = "/var/log/online-library/access.log"
errorlog = "/var/log/online-library/error.log"
loglevel = "info"

# Настройки воркеров
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2

# Настройки безопасности
forwarded_allow_ips = "*"
x_forwarded_for_header = "X-FORWARDED-FOR"

# Настройки производительности
max_requests = 1000
max_requests_jitter = 50 