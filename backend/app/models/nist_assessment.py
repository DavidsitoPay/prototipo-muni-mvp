import enum
import uuid
from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, Enum, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class NistFunction(str, enum.Enum):
    identify = "identify"
    protect = "protect"
    detect = "detect"
    respond = "respond"
    recover = "recover"


class NistAssessment(Base):
    __tablename__ = "nist_assessments"
    __table_args__ = (
        CheckConstraint("score IS NULL OR score BETWEEN 1 AND 5", name="ck_nist_score_range"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    function: Mapped[NistFunction] = mapped_column(Enum(NistFunction, name="nist_function"), nullable=False)
    question_code: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    question_text: Mapped[str] = mapped_column(String(500), nullable=False)
    score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    evaluated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
