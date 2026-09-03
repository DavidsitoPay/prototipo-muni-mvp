import enum
import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, Enum, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base
from app.models.nist_assessment import NistFunction


class RecommendationSource(str, enum.Enum):
    regla = "regla"
    llm = "llm"


class Recommendation(Base):
    __tablename__ = "recommendations"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    vulnerability_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("vulnerabilities.id"), nullable=True
    )
    nist_function: Mapped[NistFunction | None] = mapped_column(
        Enum(NistFunction, name="nist_function"), nullable=True
    )
    source: Mapped[RecommendationSource] = mapped_column(
        Enum(RecommendationSource, name="recommendation_source"), nullable=False
    )
    text: Mapped[str] = mapped_column(String(2000), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    vulnerability: Mapped["Vulnerability | None"] = relationship(back_populates="recommendations")
