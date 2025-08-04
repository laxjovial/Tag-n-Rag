import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from ..app.main import app
from ..app.database import Base, get_db
from ..app.models import User, Category

# --- Test Database Setup ---
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_categories.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

@pytest.fixture(scope="module", autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    app.dependency_overrides[get_db] = override_get_db
    yield
    Base.metadata.drop_all(bind=engine)

client = TestClient(app)

# --- Test Users ---
@pytest.fixture(scope="module")
def user_a_token():
    client.post("/auth/register", json={"username": "user_a", "password": "password_a"})
    response = client.post("/auth/login", data={"username": "user_a", "password": "password_a"})
    return response.json()["access_token"]

@pytest.fixture(scope="module")
def user_b_token():
    client.post("/auth/register", json={"username": "user_b", "password": "password_b"})
    response = client.post("/auth/login", data={"username": "user_b", "password": "password_b"})
    return response.json()["access_token"]

# --- Tests ---
def test_create_category(user_a_token):
    headers = {"Authorization": f"Bearer {user_a_token}"}
    response = client.post("/categories/", json={"name": "Category A"}, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Category A"
    assert "id" in data

def test_get_user_categories(user_a_token):
    headers = {"Authorization": f"Bearer {user_a_token}"}
    # User A should have one category from the previous test
    response = client.get("/categories/", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "Category A"

def test_user_cannot_see_other_users_categories(user_a_token, user_b_token):
    # User B creates a category
    headers_b = {"Authorization": f"Bearer {user_b_token}"}
    client.post("/categories/", json={"name": "Category B"}, headers=headers_b)

    # User A should still only see their own category
    headers_a = {"Authorization": f"Bearer {user_a_token}"}
    response = client.get("/categories/", headers=headers_a)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "Category A"

def test_user_can_delete_own_category(user_a_token):
    headers = {"Authorization": f"Bearer {user_a_token}"}
    # Get the ID of Category A
    response = client.get("/categories/", headers=headers)
    cat_id = response.json()[0]["id"]

    # Delete it
    delete_response = client.delete(f"/categories/{cat_id}", headers=headers)
    assert delete_response.status_code == 204

    # Verify it's gone
    get_response = client.get("/categories/", headers=headers)
    assert len(get_response.json()) == 0

def test_user_cannot_delete_other_users_category(user_a_token, user_b_token):
    headers_b = {"Authorization": f"Bearer {user_b_token}"}
    # Get the ID of Category B
    response = client.get("/categories/", headers=headers_b)
    cat_b_id = response.json()[0]["id"]

    # User A tries to delete it
    headers_a = {"Authorization": f"Bearer {user_a_token}"}
    delete_response = client.delete(f"/categories/{cat_b_id}", headers=headers_a)
    assert delete_response.status_code == 404 # Not found for this user
