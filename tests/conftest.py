import os

# Выставляем до импорта app, чтобы pydantic-settings не читал .env с PostgreSQL
os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["REDIS_URL"] = "redis://localhost:6379"
