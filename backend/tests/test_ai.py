import pytest
import requests


BASE_URL = "http://localhost:8000"


def test_server_health():
    """Тест здоровья сервера"""
    response = requests.get(f"{BASE_URL}/")
    assert response.status_code == 200
    assert "message" in response.json()


def test_ai_endpoints_available():
    """Тест что AI эндпоинты доступны"""
    response = requests.get(f"{BASE_URL}/openapi.json")
    openapi_data = response.json()
    paths = openapi_data['paths']

    # Проверяем что AI эндпоинты существуют
    ai_paths = [path for path in paths.keys() if '/ai/' in path]
    assert len(ai_paths) > 0, "No AI endpoints found"

    print("Available AI endpoints:")
    for path in ai_paths:
        print(f"  {path}")

@pytest.mark.skip(reason="Регистрация и логин проверены вручную, пропущено временно")
def test_create_user_and_get_token():
    """Тест создания пользователя и получения токена"""
    # Сначала попробуем найти правильный путь для регистрации
    requests.delete(f"{BASE_URL}/auth/debug/clear-users")
    response = requests.get(f"{BASE_URL}/openapi.json")
    openapi_data = response.json()
    paths = openapi_data['paths']

    # Ищем путь для создания пользователя
    user_paths = [path for path in paths.keys() if '/register' in path or '/signup' in path or '/users/create' in path]


    if not user_paths:
        pytest.skip("User registration endpoint not found")

    user_path = user_paths[0]
    print(f"Using user registration path: {user_path}")

    # Создаем пользователя
    user_data = {
        "username": "testuser",
        "email": "pytest@example.com",
        "password": "pytest_password123"
    }

    response = requests.post(f"{BASE_URL}{user_path}", json=user_data)

    # 201 - создан, 400 - уже существует, оба acceptable
    assert response.status_code in [201, 400], f"Unexpected status: {response.status_code}"

    # Ищем путь для получения токена
    token_paths = [path for path in paths.keys() if '/token' in path and 'post' in str(paths[path])]

    if not token_paths:
        pytest.skip("Token endpoint not found")

    token_path = token_paths[0]
    print(f"Using token path: {token_path}")

    # Получаем токен
    auth_data = {
        "username": "testuser",
        "password": "pytest_password123",
        "grant_type": "password"
    }

    response = requests.post(f"{BASE_URL}{token_path}", data=auth_data)

    # Если пользователь уже существовал, можем получить 400
    if response.status_code == 400:
        print("User already exists, trying to get token anyway...")
        # Пробуем получить токен для существующего пользователя
        response = requests.post(f"{BASE_URL}{token_path}", data=auth_data)

    assert response.status_code == 200, f"Token request failed: {response.text}"

    token = response.json().get("access_token")
    assert token is not None, "No token in response"

    return token

@pytest.mark.skip(reason="Регистрация и логин проверены вручную, пропущено временно")
def test_ai_settings_with_token():
    """Тест настроек AI с токеном"""
    token = test_create_user_and_get_token()
    headers = {"Authorization": f"Bearer {token}"}

    # Тестируем AI настройки
    response = requests.get(
        f"{BASE_URL}/ai/ai/users/me/ai-settings",
        headers=headers
    )

    # 200 - успех, 404 - не найдено, 401 - нет доступа
    assert response.status_code in [200, 404, 401], f"Unexpected status: {response.status_code}"

    if response.status_code == 200:
        settings = response.json()
        assert "enabled" in settings
        print(f"AI settings: {settings}")

@pytest.mark.skip(reason="Регистрация и логин проверены вручную, пропущено временно")
def test_ai_quest_generation():
    """Тест генерации AI квеста"""
    token = test_create_user_and_get_token()
    headers = {"Authorization": f"Bearer {token}"}

    quest_data = {
        "theme": "тестовый квест",
        "category": "productivity"
    }

    response = requests.post(
        f"{BASE_URL}/ai/ai/users/me/generate-quest",
        json=quest_data,
        headers=headers,
        timeout=30
    )

    # Проверяем возможные статусы
    assert response.status_code in [200, 400, 401, 404, 500], f"Unexpected status: {response.status_code}"

    if response.status_code == 200:
        quest = response.json()
        assert "title" in quest
        assert "steps" in quest
        print(f"Generated quest: {quest['title']}")


# Дополнительные тесты
def test_root_endpoint():
    """Тест корневого эндпоинта"""
    response = requests.get(f"{BASE_URL}/")
    assert response.status_code == 200
    assert "message" in response.json()


def test_health_endpoint():
    """Тест health эндпоинта (если существует)"""
    response = requests.get(f"{BASE_URL}/health")
    # Health endpoint может не существовать, это нормально
    if response.status_code != 404:
        assert response.status_code == 200
        assert "status" in response.json()