import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.backend.main import app
from src.backend.data.database import Base, get_db
from src.backend.data.models import User

# --- Test Database Setup ---
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_user_mgmt.db"
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
def admin_token():
    client.post("/auth/register", json={"username": "mgmt_admin", "password": "password"})
    db = TestingSessionLocal()
    user = db.query(User).filter(User.username == "mgmt_admin").first()
    user.role = "admin"
    db.commit()
    db.close()
    response = client.post("/auth/login", data={"username": "mgmt_admin", "password": "password"})
    return response.json()["access_token"]

@pytest.fixture(scope="module")
def regular_user_token():
    client.post("/auth/register", json={"username": "mgmt_user", "password": "password"})
    response = client.post("/auth/login", data={"username": "mgmt_user", "password": "password"})
    return response.json()["access_token"]

# --- Tests ---
def test_admin_can_invite_user(admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    payload = {"username": "invited_user", "email": "invited@example.com"}
    response = client.post("/admin/users/invite", json=payload, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "invited_user"
    assert data["role"] == "user"

def test_admin_can_update_role(admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    # Get the ID of the user to update
    user_id = client.get("/admin/users/", headers=headers).json()[0]['id']

    payload = {"role": "admin"}
    response = client.put(f"/admin/users/{user_id}/role", json=payload, headers=headers)
    assert response.status_code == 200
    assert response.json()["role"] == "admin"

def test_admin_can_delete_user(admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    # Invite a user specifically for deletion to avoid conflicts
    client.post("/admin/users/invite", json={"username": "user_to_delete", "email": "del@test.com"}, headers=headers)

    # Get the new user's ID
    users = client.get("/admin/users/", headers=headers).json()
    user_to_delete = next(u for u in users if u['username'] == 'user_to_delete')
    user_id = user_to_delete['id']

    response = client.delete(f"/admin/users/{user_id}", headers=headers)
    assert response.status_code == 204

    # Verify the user is gone
    users_after_delete = client.get("/admin/users/", headers=headers).json()
    assert user_id not in [u['id'] for u in users_after_delete]

def test_regular_user_cannot_invite(regular_user_token):
    headers = {"Authorization": f"Bearer {regular_user_token}"}
    payload = {"username": "test", "email": "test@test.com"}
    response = client.post("/admin/users/invite", json=payload, headers=headers)
    assert response.status_code == 403
