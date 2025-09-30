import pytest
import asyncio
from datetime import timedelta

from fastapi import HTTPException
from jose import jwt

from backend.app import security
from backend.app.database import models


# ---------- FIXTURES ----------

class DummyDB:
    """Фейковая база для тестов"""
    def __init__(self, users):
        self.users = users

    def query(self, model):
        return self

    def filter(self, condition):
        username = condition.right.value  # достаем имя из фильтра
        user = next((u for u in self.users if u.username == username), None)
        return DummyQuery(user)


class DummyQuery:
    def __init__(self, user):
        self.user = user

    def first(self):
        return self.user


@pytest.fixture
def fake_user():
    return models.Player(
        id=1,
        username="testuser",
        hashed_password=security.get_password_hash("password"),
        email="test@example.com",
        is_active=True,
    )


@pytest.fixture
def dummy_db(fake_user):
    return DummyDB([fake_user])


def make_token(username: str):
    data = {"sub": username}
    return security.create_access_token(data, expires_delta=timedelta(minutes=5))


# ---------- TESTS ----------

def test_get_current_user_valid(dummy_db, fake_user):
    token = make_token(fake_user.username)
    user = asyncio.run(security.get_current_user(token=token, db=dummy_db))
    assert user.username == fake_user.username


def test_get_current_user_invalid_token(dummy_db):
    with pytest.raises(HTTPException) as excinfo:
        asyncio.run(security.get_current_user(token="invalid.token", db=dummy_db))
    assert excinfo.value.status_code == 401


def test_get_current_user_nonexistent(dummy_db):
    token = make_token("ghostuser")
    with pytest.raises(HTTPException) as excinfo:
        asyncio.run(security.get_current_user(token=token, db=dummy_db))
    assert excinfo.value.status_code == 401


def test_get_current_active_user_active(fake_user):
    user = security.get_current_active_user(fake_user)
    assert user.username == "testuser"


def test_get_current_active_user_inactive(fake_user):
    fake_user.is_active = False
    with pytest.raises(HTTPException) as excinfo:
        security.get_current_active_user(fake_user)
    assert excinfo.value.status_code == 400


def test_password_hash_and_verify():
    password = "supersecret"
    hashed = security.get_password_hash(password)

    assert hashed != password
    assert security.verify_password(password, hashed) is True
    assert security.verify_password("wrongpass", hashed) is False


def test_create_access_token_and_decode():
    data = {"sub": "testuser"}
    token = security.create_access_token(data, expires_delta=timedelta(minutes=5))

    payload = jwt.decode(token, security.SECRET_KEY, algorithms=[security.ALGORITHM])
    assert payload.get("sub") == "testuser"


def test_create_refresh_token_and_verify():
    data = {"sub": "refreshuser"}
    token = security.create_refresh_token(data, expires_delta=timedelta(days=1))

    sub = security.verify_refresh_token(token)
    assert sub == "refreshuser"


def test_verify_refresh_token_invalid():
    invalid_token = "this.is.not.a.jwt"
    payload = security.verify_refresh_token(invalid_token)

    assert payload is None


def test_create_email_token_and_verify():
    data = {"sub": "test@example.com"}
    token = security.create_email_token(data)

    email = security.verify_email_token(token)
    assert email == "test@example.com"


def test_verify_email_token_invalid():
    invalid_token = "broken.token.here"
    email = security.verify_email_token(invalid_token)

    assert email is None
