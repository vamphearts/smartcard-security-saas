"""Audit logging for Smart-card access events."""
from datetime import datetime
from typing import Any

from sqlalchemy import Column, DateTime, Float, Integer, String, Text, create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker


class Base(DeclarativeBase):
    pass


class AuditLog(Base):
    __tablename__ = "audit_log"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(64), nullable=False)
    card_id = Column(String(64), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    failed_pin_count = Column(Integer, default=0)
    requests_per_min = Column(Float, default=0.0)
    access_granted = Column(Integer, default=0)
    label = Column(String(32), default="unknown")
    anomaly_score = Column(Float, nullable=True)
    decision = Column(String(64), nullable=True)
    details = Column(Text, nullable=True)


def init_schema(database_url: str | None = None) -> None:
    """Create tables once before gunicorn workers start."""
    import os

    url = database_url or os.getenv(
        "DATABASE_URL",
        "postgresql://app:smartcard_secret@db:5432/smartcard_db",
    )
    engine = create_engine(url, pool_pre_ping=True)
    Base.metadata.create_all(engine, checkfirst=True)


class AuditLogger:
    def __init__(self, database_url: str):
        self.engine = create_engine(database_url, pool_pre_ping=True)
        self.SessionLocal = sessionmaker(bind=self.engine)

    def log_event(self, record: dict[str, Any]) -> int:
        with Session(self.engine) as session:
            row = AuditLog(
                session_id=record["session_id"],
                card_id=record["card_id"],
                timestamp=record.get("timestamp", datetime.utcnow()),
                failed_pin_count=int(record.get("failed_pin_count", 0)),
                requests_per_min=float(record.get("requests_per_min", 0)),
                access_granted=int(record.get("access_granted", 0)),
                label=str(record.get("label", "unknown")),
                anomaly_score=record.get("anomaly_score"),
                decision=record.get("decision"),
                details=record.get("details"),
            )
            session.add(row)
            session.commit()
            session.refresh(row)
            return row.id

    def list_recent(self, limit: int = 50) -> list[dict]:
        with Session(self.engine) as session:
            rows = (
                session.query(AuditLog)
                .order_by(AuditLog.id.desc())
                .limit(limit)
                .all()
            )
            return [
                {
                    "id": r.id,
                    "session_id": r.session_id,
                    "card_id": r.card_id,
                    "timestamp": r.timestamp.isoformat() if r.timestamp else None,
                    "failed_pin_count": r.failed_pin_count,
                    "requests_per_min": r.requests_per_min,
                    "access_granted": r.access_granted,
                    "label": r.label,
                    "anomaly_score": r.anomaly_score,
                    "decision": r.decision,
                }
                for r in rows
            ]
