from sqlalchemy import ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base

class BehaviorMetrics(Base):
    """CREATE TABLE behavior_metrics (application_id INTEGER PRIMARY KEY REFERENCES applications(id)
    ON DELETE CASCADE, time_on_page INTEGER NOT NULL, visits INTEGER NOT NULL,
    clicks JSON NOT NULL, pointer_samples JSON NOT NULL, technical JSON NOT NULL);"""
    __tablename__ = "behavior_metrics"
    application_id: Mapped[int] = mapped_column(ForeignKey("applications.id", ondelete="CASCADE"), primary_key=True)
    time_on_page: Mapped[int]
    visits: Mapped[int]
    clicks: Mapped[list] = mapped_column(JSON)
    pointer_samples: Mapped[list] = mapped_column(JSON)
    technical: Mapped[dict] = mapped_column(JSON)

class MetricsCRUD:
    @staticmethod
    def get(db, application_id):
        return db.get(BehaviorMetrics, application_id)
