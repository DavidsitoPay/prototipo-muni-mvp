import enum
import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, Enum, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class AssetType(str, enum.Enum):
    servidor = "servidor"
    aplicacion = "aplicacion"
    base_datos = "base_datos"
    red = "red"
    endpoint = "endpoint"
    sistema_web_publico = "sistema_web_publico"


class AssetCriticality(str, enum.Enum):
    baja = "baja"
    media = "media"
    alta = "alta"
    critica = "critica"


class AssetStatus(str, enum.Enum):
    activo = "activo"
    mantenimiento = "mantenimiento"
    dado_de_baja = "dado_de_baja"


class AssetLocation(str, enum.Enum):
    fisico = "fisico"
    nube = "nube"
    on_prem = "on_prem"


class Asset(Base):
    __tablename__ = "assets"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    type: Mapped[AssetType] = mapped_column(Enum(AssetType, name="asset_type"), nullable=False)
    department: Mapped[str] = mapped_column(String(150), nullable=False)
    criticality: Mapped[AssetCriticality] = mapped_column(
        Enum(AssetCriticality, name="asset_criticality"), nullable=False
    )
    status: Mapped[AssetStatus] = mapped_column(
        Enum(AssetStatus, name="asset_status"), default=AssetStatus.activo, nullable=False
    )
    owner: Mapped[str] = mapped_column(String(150), nullable=False)
    location: Mapped[AssetLocation] = mapped_column(Enum(AssetLocation, name="asset_location"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, default=None)

    vulnerabilities: Mapped[list["Vulnerability"]] = relationship(
        back_populates="asset", cascade="all, delete-orphan"
    )
    business_metrics: Mapped[list["DemoBusinessMetric"]] = relationship(
        back_populates="asset", cascade="all, delete-orphan"
    )
