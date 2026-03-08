import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from unittest.mock import patch

from app.main import app
from app.database import Base, get_db

# StaticPool нужен для SQLite in-memory: без него каждое соединение
# получает свою отдельную пустую БД, и таблицы не видны между вызовами
SQLALCHEMY_TEST_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_TEST_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


client = TestClient(app)


def test_cache_miss_then_cache_set():
    """При первом запросе поста — данных в кеше нет, после запроса они туда кладутся"""
    # Создаём пост
    resp = client.post("/posts/", json={"title": "Тест", "content": "Содержимое"})
    assert resp.status_code == 201
    post_id = resp.json()["id"]

    with patch("app.cache.get_cached_post", return_value=None) as mock_get, \
         patch("app.cache.set_cached_post") as mock_set:

        resp = client.get(f"/posts/{post_id}")
        assert resp.status_code == 200

        mock_get.assert_called_once_with(post_id)
        mock_set.assert_called_once()


def test_cache_hit_skips_db():
    """При повторном запросе данные берутся из кеша, в БД не ходим"""
    fake_post = {
        "id": 1,
        "title": "Из кеша",
        "content": "Содержимое",
        "created_at": "2024-01-01T00:00:00",
        "updated_at": "2024-01-01T00:00:00",
    }

    with patch("app.cache.get_cached_post", return_value=fake_post) as mock_get:
        resp = client.get("/posts/1")
        assert resp.status_code == 200
        assert resp.json()["title"] == "Из кеша"
        mock_get.assert_called_once_with(1)


def test_cache_invalidated_on_update():
    """При обновлении поста кеш должен удаляться"""
    resp = client.post("/posts/", json={"title": "Старый", "content": "Текст"})
    post_id = resp.json()["id"]

    with patch("app.cache.delete_cached_post") as mock_delete:
        resp = client.patch(f"/posts/{post_id}", json={"title": "Новый"})
        assert resp.status_code == 200
        assert resp.json()["title"] == "Новый"
        mock_delete.assert_called_once_with(post_id)


def test_cache_invalidated_on_delete():
    """При удалении поста кеш должен удаляться"""
    resp = client.post("/posts/", json={"title": "Удаляемый", "content": "Текст"})
    post_id = resp.json()["id"]

    with patch("app.cache.delete_cached_post") as mock_delete:
        resp = client.delete(f"/posts/{post_id}")
        assert resp.status_code == 204
        mock_delete.assert_called_once_with(post_id)


def test_get_nonexistent_post():
    """Запрос несуществующего поста возвращает 404"""
    with patch("app.cache.get_cached_post", return_value=None):
        resp = client.get("/posts/9999")
        assert resp.status_code == 404
