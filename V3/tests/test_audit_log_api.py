import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.backend.main import app
from src.backend.data.database import Base, get_db
from src.backend.data.models import User, AuditLog

# --- Test Database Setup ---
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_audit.db"
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
def admin_user_token():
    client.post("/auth/register", json={"username": "audit_admin", "password": "password"})
    db = TestingSessionLocal()
    admin_user = db.query(User).filter(User.username == "audit_admin").first()
    admin_user.role = "admin"
    db.commit()
    db.close()
    response = client.post("/auth/login", data={"username": "audit_admin", "password": "password"})
    return response.json()["access_token"]

@pytest.fixture(scope="module")
def regular_user_token():
    client.post("/auth/register", json={"username": "audit_user", "password": "password"})
    response = client.post("/auth/login", data={"username": "audit_user", "password": "password"})
    return response.json()["access_token"]

# --- Tests ---
def test_login_creates_audit_log():
    db = TestingSessionLocal()
    log_count_before = db.query(AuditLog).count()

    # This login is from the fixture, so we need another one to test the trigger
    client.post("/auth/login", data={"username": "audit_user", "password": "password"})

    log_count_after = db.query(AuditLog).count()
    assert log_count_after > log_count_before

    latest_log = db.query(AuditLog).order_by(AuditLog.id.desc()).first()
    assert latest_log.action == "user_login"
    assert latest_log.user.username == "audit_user"
    db.close()

def test_admin_can_get_audit_log(admin_user_token):
    headers = {"Authorization": f"Bearer {admin_user_token}"}
    response = client.get("/admin/audit-log/", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert "action" in data[0]
    assert "username" in data[0]

def test_regular_user_cannot_get_audit_log(regular_user_token):
    headers = {"Authorization": f"Bearer {regular_user_token}"}
    response = client.get("/admin/audit-log/", headers=headers)
    assert response.status_code == 403
