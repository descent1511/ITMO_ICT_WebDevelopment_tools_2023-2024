# Docker-compose
```yml
version: '3.9'

networks:
  app-network:

services:
  celery_app:
    build:
      context: ./celery
      dockerfile: Dockerfile
    container_name: celery
    restart: always
    ports:
      - "3000:3000"
    networks:
      - app-network
    depends_on:
      - redis

  celery_worker:
    build:
      context: ./celery
    container_name: celery_worker
    command: celery -A celery_worker worker --loglevel=info
    restart: always
    networks:
      - app-network
    depends_on:
      - redis
      - celery_app

  redis:
    image: redis:7.2.4
    container_name: redis
    ports:
      - "6379:6379"
    restart: always
    networks:
      - app-network

  fastapi:
    build: ./fast-api
    ports:
      - "8000:8000"
    environment:
      DB_USER: ${DB_USER}
      DB_NAME: ${DB_NAME}
      DB_PASS: ${DB_PASS}
      DB_HOST: "db"
      JWT_SECRET_KEY: ${JWT_SECRET_KEY}
      JWT_REFRESH_SECRET_KEY: ${JWT_REFRESH_SECRET_KEY}
      CELERY_HOST: celery_app
      CELERY_PORT: "3000"
    depends_on:
      - db
      - celery_app
    networks:
      - app-network

  db:
    image: postgres:latest
    ports:
      - "5432:5432"
    environment:
      POSTGRES_USER: ${DB_USER}
      POSTGRES_PASSWORD: ${DB_PASS}
      POSTGRES_DB: ${DB_NAME}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - app-network
    
volumes:
  postgres_data:

```
## Объяснение 

### Networks
#### `app-network`
   Определяет пользовательскую сеть с именем `app-network`, которая используется для связи между контейнерами.

### Services

#### Celery_app
1. `build:`
   - `context: ./celery`
     Определяет путь к директории с исходным кодом приложения Celery.
   - `dockerfile: Dockerfile`
     Указывает имя Dockerfile, который будет использоваться для сборки образа.

2. `container_name: celery`
   Устанавливает имя контейнера как `celery`.

3. `restart: always`
   Настраивает контейнер на автоматический перезапуск в случае сбоя.

4. `ports:`
   - `"3000:3000"`
     Пробрасывает порт 3000 на хосте к порту 3000 внутри контейнера.

5. `networks:`
   - `app-network`
     Подключает контейнер к сети `app-network`.

6. `depends_on:`
   - `redis`
     Указывает, что контейнер `celery_app` зависит от контейнера `redis` и должен запускаться после него.

#### Celery_worker
1. `build:`
   - `context: ./celery`
     Определяет путь к директории с исходным кодом приложения Celery Worker.

2. `container_name: celery_worker`
   Устанавливает имя контейнера как `celery_worker`.

3. `command: celery -A celery_worker worker --loglevel=info`
   Запускает команду для старта Celery Worker с указанием уровня логирования `info`.

4. `restart: always`
   Настраивает контейнер на автоматический перезапуск в случае сбоя.

5. `networks:`
   - `app-network`
     Подключает контейнер к сети `app-network`.

6. `depends_on:`
   - `redis`
   - `celery_app`
     Указывает, что контейнер `celery_worker` зависит от контейнеров `redis` и `celery_app` и должен запускаться после них.

#### Redis
1. `image: redis:7.2.4`
   Использует официальный образ Redis версии 7.2.4.

2. `container_name: redis`
   Устанавливает имя контейнера как `redis`.

3. `ports:`
   - `"6379:6379"`
     Пробрасывает порт 6379 на хосте к порту 6379 внутри контейнера.

4. `restart: always`
   Настраивает контейнер на автоматический перезапуск в случае сбоя.

5. `networks:`
   - `app-network`
     Подключает контейнер к сети `app-network`.

#### Fastapi
1. `build: ./fast-api`
   Определяет путь к директории с исходным кодом FastAPI приложения.

2. `ports:`
   - `"8000:8000"`
     Пробрасывает порт 8000 на хосте к порту 8000 внутри контейнера.

3. `environment:`
   Определяет переменные окружения для контейнера:
   - `DB_USER: ${DB_USER}`
   - `DB_NAME: ${DB_NAME}`
   - `DB_PASS: ${DB_PASS}`
   - `DB_HOST: "db"`
   - `JWT_SECRET_KEY: ${JWT_SECRET_KEY}`
   - `JWT_REFRESH_SECRET_KEY: ${JWT_REFRESH_SECRET_KEY}`
   - `CELERY_HOST: celery_app`
   - `CELERY_PORT: "3000"`

4. `depends_on:`
   - `db`
   - `celery_app`
     Указывает, что контейнер `fastapi` зависит от контейнеров `db` и `celery_app` и должен запускаться после них.

5. `networks:`
   - `app-network`
     Подключает контейнер к сети `app-network`.

#### DB
1. `image: postgres:latest`
   Использует официальный образ Postgres последней версии.

2. `ports:`
   - `"5432:5432"`
     Пробрасывает порт 5432 на хосте к порту 5432 внутри контейнера.

3. `environment:`
   Определяет переменные окружения для контейнера:
   - `POSTGRES_USER: ${DB_USER}`
   - `POSTGRES_PASSWORD: ${DB_PASS}`
   - `POSTGRES_DB: ${DB_NAME}`

4. `volumes:`
   - `postgres_data:/var/lib/postgresql/data`
     Подключает том `postgres_data` к директории `/var/lib/postgresql/data` внутри контейнера для сохранения данных базы данных.

5. `networks:`
   - `app-network`
     Подключает контейнер к сети `app-network`.




