# Blog API

REST API для блога с кешированием постов через Redis.

## Стек

- **FastAPI** — веб-фреймворк
- **PostgreSQL** — основная БД
- **Redis** — кеш
- **SQLAlchemy** — ORM
- **pytest** — тесты

## Архитектура

```
Клиент
   │
   ▼
FastAPI (app)
   │
   ├── GET /posts/{id} ──► Redis (кеш)
   │                          │ miss
   │                          ▼
   │                       PostgreSQL
   │                          │
   │                     сохранить в кеш
   │
   ├── POST /posts/  ──────► PostgreSQL
   │
   ├── PATCH /posts/{id} ──► PostgreSQL + удалить из Redis
   │
   └── DELETE /posts/{id} ─► PostgreSQL + удалить из Redis
```

**Почему такой подход к кешированию:**
- Кешируем на уровне отдельного поста (ключ `post:{id}`) — просто инвалидировать при изменении
- TTL = 5 минут (настраивается через `.env`) — баланс между актуальностью и нагрузкой на БД
- Инвалидация при PATCH/DELETE — данные не протухают после изменений

## Запуск через Docker

```bash
cp .env.example .env
docker-compose up --build
```

API будет доступно на `http://localhost:8000`
Документация: `http://localhost:8000/docs`

## Запуск локально

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env
# Отредактируй .env под свои параметры БД и Redis

uvicorn app.main:app --reload
```

## Эндпоинты

| Метод | URL | Описание |
|-------|-----|----------|
| POST | `/posts/` | Создать пост |
| GET | `/posts/` | Список всех постов |
| GET | `/posts/{id}` | Получить пост (с кешем) |
| PATCH | `/posts/{id}` | Обновить пост |
| DELETE | `/posts/{id}` | Удалить пост |
| GET | `/health` | Проверка работоспособности |

## Тесты

```bash
pip install -r requirements.txt
pytest tests/ -v
```

Тесты используют SQLite in-memory и мокают Redis — реальные сервисы не нужны.
