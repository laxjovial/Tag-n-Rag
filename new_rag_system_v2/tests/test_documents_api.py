import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from ..app.main import app
from ..app.database import Base, get_db
from ..app.services.storage import CloudStorageService
from unittest.mock import MagicMock

# --- Test Database Setup ---
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

# --- Mock GCS Service ---
@pytest.fixture
def mock_gcs():
    mock = MagicMock(spec=CloudStorageService)
    mock.upload.return_value = None
    mock.delete.return_value = None
    return mock

client = TestClient(app)

@pytest.fixture(scope="module")
def test_user_token():
    # Create a test user
    response = client.post("/auth/register", json={"username": "testuser_docs", "password": "password"})
    assert response.status_code == 200

    # Log in to get a token
    response = client.post("/auth/login", data={"username": "testuser_docs", "password": "password"})
    assert response.status_code == 200
    return response.json()["access_token"]

def test_create_document_from_text(test_user_token, mock_gcs):
    app.dependency_overrides[CloudStorageService] = lambda: mock_gcs

    headers = {"Authorization": f"Bearer {test_user_token}"}
    payload = {
        "filename": "test_doc.txt",
        "content": "This is a test document.",
    }
    response = client.post("/documents/from_text", json=payload, headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert data["original_filename"] == "test_doc.txt"
    assert data["owner_id"] is not None
    mock_gcs.upload.assert_called_once()

def test_delete_document(test_user_token, mock_gcs):
    app.dependency_overrides[CloudStorageService] = lambda: mock_gcs

    # First, create a document to delete
    headers = {"Authorization": f"Bearer {test_user_token}"}
    payload = {"filename": "doc_to_delete.txt", "content": "delete me"}
    create_response = client.post("/documents/from_text", json=payload, headers=headers)
    assert create_response.status_code == 200
    doc_id = create_response.json()["id"]

    # Now, delete it
    delete_response = client.delete(f"/documents/{doc_id}", headers=headers)
    assert delete_response.status_code == 204
    mock_gcs.delete.assert_called_once()

    # Verify it's gone
    get_response = client.get(f"/documents/{doc_id}", headers=headers)
    assert get_response.status_code == 404
