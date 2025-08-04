from sqlalchemy.orm import Session
from src.backend.data.models import AuditLog, User

def create_audit_log(
    db: Session,
    user: User,
    action: str,
    details: dict = None
):
    """
    Creates an entry in the audit log.
    """
    log_entry = AuditLog(
        user_id=user.id if user else None,
        action=action,
        details=details
    )
    db.add(log_entry)
    db.commit()
