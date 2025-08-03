import time
import threading
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from ..database import SessionLocal
from ..models import Document, Notification # Corrected: Import Document from .models
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


def check_and_notify_expiring_documents(warning_days: int = 7):
    """
    Checks for documents that are expiring soon and notifies the owner.
    """
    db: Session = SessionLocal()
    try:
        warning_date = datetime.utcnow() + timedelta(days=warning_days)
        expiring_docs = db.query(Document).filter(
            Document.expires_at != None,
            Document.expires_at <= warning_date
        ).all()

        for doc in expiring_docs:
            # Avoid sending duplicate notifications
            existing_notif = db.query(Notification).filter_by(
                user_id=doc.owner_id,
                message=f"Your document '{doc.original_filename}' is set to expire on {doc.expires_at.date()}."
            ).first()

            if not existing_notif:
                notification = Notification(
                    user_id=doc.owner_id,
                    message=f"Your document '{doc.original_filename}' is set to expire on {doc.expires_at.date()}."
                )
                db.add(notification)
                print(f"Created expiration warning for user {doc.owner_id} for document {doc.id}")
        db.commit()
    finally:
        db.close()


def run_background_services(interval_seconds: int = 3600):
    """
    Runs all periodic background services.
    """
    while True:
        print("Running background services...")
        check_and_delete_expired_documents()
        check_and_notify_expiring_documents()
        print("Background services finished. Sleeping...")
        time.sleep(interval_seconds)


def start_background_tasks():
    """
    Starts the background services in a separate thread.
    """
    background_thread = threading.Thread(target=run_background_services, daemon=True)
    background_thread.start()
    print("Background services started.")
