# tests/simple_test.py
import requests

BASE_URL = "http://localhost:8000"


def test_basic():
    print("🧪 Basic API test")

    # 1. Проверка корневого эндпоинта
    print("1. Testing root endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"   ❌ Error: {e}")

    # 2. Проверка документации
    print("\n2. Testing docs...")
    try:
        response = requests.get(f"{BASE_URL}/docs", timeout=5)
        print(f"   Docs status: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {e}")

    # 3. Проверка OpenAPI spec
    print("\n3. Testing OpenAPI spec...")
    try:
        response = requests.get(f"{BASE_URL}/openapi.json", timeout=5)
        print(f"   OpenAPI status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            paths = list(data['paths'].keys())
            print("   Available endpoints:")
            for path in sorted(paths):
                if any(x in path for x in ['/ai/', '/users/', '/token']):
                    print(f"     {path}")
    except Exception as e:
        print(f"   ❌ Error: {e}")

    print("\n✅ Basic test completed!")


if __name__ == "__main__":
    test_basic()