import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from ..app.main import app
from ..app.database import Base, get_db
from ..app.models import User

# --- Test Database Setup ---
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_auth.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Apply the same dependency override as in other test files
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

@pytest.fixture(scope="module", autouse=True)
def apply_db_override():
    Base.metadata.create_all(bind=engine)
    app.dependency_overrides[get_db] = override_get_db
    yield
    Base.metadata.drop_all(bind=engine)

client = TestClient(app)

# --- Test Users ---
@pytest.fixture(scope="module")
def regular_user_token():
    # Register and login a regular user
    client.post("/auth/register", json={"username": "testuser_regular", "password": "password"})
    response = client.post("/auth/login", data={"username": "testuser_regular", "password": "password"})
    return response.json()["access_token"]

@pytest.fixture(scope="module")
def admin_user_token():
    # Register an admin user
    client.post("/auth/register", json={"username": "testuser_admin", "password": "password"})

    # Manually update the user's role to 'admin' in the test DB
    db = TestingSessionLocal()
    admin_user = db.query(User).filter(User.username == "testuser_admin").first()
    admin_user.role = "admin"
    db.commit()
    db.close()

    # Login the admin user
    response = client.post("/auth/login", data={"username": "testuser_admin", "password": "password"})
    return response.json()["access_token"]


# --- Tests ---
def test_register_user():
    response = client.post("/auth/register", json={"username": "test_register", "password": "password"})
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "test_register"
    assert data["role"] == "user" # Should default to 'user'

def test_login_user():
    response = client.post("/auth/login", data={"username": "testuser_regular", "password": "password"})
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_admin_can_access_admin_route(admin_user_token):
    headers = {"Authorization": f"Bearer {admin_user_token}"}
    response = client.get("/admin/users/", headers=headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_regular_user_cannot_access_admin_route(regular_user_token):
    headers = {"Authorization": f"Bearer {regular_user_token}"}
    response = client.get("/admin/users/", headers=headers)
    assert response.status_code == 403 # Forbidden
    assert response.json()["detail"] == "Not an admin user"

def test_unauthenticated_cannot_access_protected_route():
    response = client.get("/admin/users/")
    assert response.status_code == 401 # Unauthorized

def test_get_current_user(regular_user_token):
    headers = {"Authorization": f"Bearer {regular_user_token}"}
    response = client.get("/user/me", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "testuser_regular"
