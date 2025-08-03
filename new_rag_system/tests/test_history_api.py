import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta
from ..app.main import app
from ..app.database import Base, get_db
from ..app.models import User, QueryLog, Document

# --- Test Database Setup ---
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_history.db"
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
    Base.metadata.drop_all(bind=engine) # Ensure clean state
    Base.metadata.create_all(bind=engine)
    app.dependency_overrides[get_db] = override_get_db
    yield
    Base.metadata.drop_all(bind=engine)

client = TestClient(app)

# --- Test User and Data ---
@pytest.fixture(scope="module")
def history_user_token():
    # Register user
    client.post("/auth/register", json={"username": "history_user", "password": "password"})

    # Login the user to get a token
    response = client.post("/auth/login", data={"username": "history_user", "password": "password"})
    token = response.json()["access_token"]

    # Now, create data for this logged-in user
    db = TestingSessionLocal()
    user = db.query(User).filter(User.username == "history_user").first()

    doc = Document(filename="hist_doc.txt", original_filename="hist_doc.txt", owner_id=user.id)
    db.add(doc)
    db.commit()
    db.refresh(doc)

    # Create some query logs for this user
    db.add(QueryLog(question="Q1", answer_text="A1", user_id=user.id, document_id=doc.id, created_at=datetime.utcnow() - timedelta(days=2)))
    db.add(QueryLog(question="Q2", answer_text="A2", user_id=user.id, document_id=doc.id, created_at=datetime.utcnow() - timedelta(days=1)))
    db.add(QueryLog(question="Q3", answer_text="A3", user_id=user.id, document_id=doc.id, created_at=datetime.utcnow() - timedelta(days=1)))
    db.commit()
    db.close()

    return token

# --- Tests ---
def test_get_user_history(history_user_token):
    headers = {"Authorization": f"Bearer {history_user_token}"}
    response = client.get("/history/", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3
    assert data[0]["question"] == "Q3" # Most recent first

def test_get_user_analytics(history_user_token):
    headers = {"Authorization": f"Bearer {history_user_token}"}
    response = client.get("/history/analytics", headers=headers)
    assert response.status_code == 200
    data = response.json()

    assert data["total_queries"] == 3

    assert len(data["queries_per_day"]) == 2
    assert data["queries_per_day"][0]["queries"] == 1 # 2 days ago
    assert data["queries_per_day"][1]["queries"] == 2 # 1 day ago

    assert len(data["top_documents"]) == 1
    assert data["top_documents"][0]["count"] == 3
