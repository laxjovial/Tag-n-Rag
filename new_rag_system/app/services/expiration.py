import time
import threading
from datetime import datetime
from sqlalchemy.orm import Session
from ..database import SessionLocal, Document
from ..rag import RAGSystem

def check_and_delete_expired_documents():
    """
    Checks for and deletes expired documents.
    This function is intended to be run periodically in a background thread.
    """
    db: Session = SessionLocal()
    rag_system = RAGSystem() # It's better to pass this as an argument if it has state

    try:
        now = datetime.utcnow()
        expired_documents = db.query(Document).filter(
            Document.expires_at != None,
            Document.expires_at < now
        ).all()

        if expired_documents:
            print(f"Found {len(expired_documents)} expired documents to delete.")
            for doc in expired_documents:
                print(f"Deleting document {doc.id} ('{doc.filename}')")
                # 1. Delete from vector store
                rag_system.delete_document(document_id=doc.id)
                # 2. Delete from database
                db.delete(doc)
            db.commit()
    finally:
        db.close()

def run_expiration_service(interval_seconds: int = 3600):
    """
    Runs the expiration check periodically.

    Args:
        interval_seconds (int): The interval in seconds to wait between checks.
                                Defaults to 1 hour.
    """
    while True:
        check_and_delete_expired_documents()
        time.sleep(interval_seconds)

def start_background_tasks():
    """
    Starts the background services in a separate thread.
    """
    # Run the expiration service in a daemon thread so it doesn't block exit
    expiration_thread = threading.Thread(target=run_expiration_service, daemon=True)
    expiration_thread.start()
    print("Document expiration service started in the background.")
