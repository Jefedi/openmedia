"""Modèles pour la disponibilité sur les plateformes de streaming"""
from datetime import datetime, date
from typing import Optional
from decimal import Decimal

from sqlalchemy import (
    String, Integer, Numeric, Date, DateTime, Boolean,
    ForeignKey, UniqueConstraint, Index, CheckConstraint
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class Platform(Base):
    """Plateformes de streaming / location / achat"""

    __tablename__ = "platforms"

    # Identifiant externe (ex: JustWatch provider_id, TMDB network_id)
    external_id: Mapped[Optional[int]] = mapped_column(Integer, unique=True, index=True, nullable=True)

    # Informations
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    slug: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)

    # Type de plateforme
    platform_type: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="subscription"  # subscription, rent, buy, free
    )

    # Logo
    logo_path: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # URL du site
    website_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # Pays de disponibilité (codes ISO)
    available_countries: Mapped[Optional[list]] = mapped_column(
        String,  # JSON array
        nullable=True
    )

    # Actif
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Priorité d'affichage
    display_priority: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Relations
    availabilities: Mapped[list["Availability"]] = relationship(
        "Availability",
        back_populates="platform",
        cascade="all, delete-orphan"
    )

    __table_args__ = (
        CheckConstraint(
            "platform_type IN ('subscription', 'rent', 'buy', 'free')",
            name="check_platform_type"
        ),
    )

    def __repr__(self) -> str:
        return f"Platform(id={self.id}, name={self.name}, type={self.platform_type})"


class Availability(Base):
    """Disponibilité d'un média sur une plateforme"""

    __tablename__ = "availabilities"

    # Relations
    platform_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("platforms.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    platform: Mapped["Platform"] = relationship("Platform", back_populates="availabilities")

    # Type de média
    media_type: Mapped[str] = mapped_column(String(10), nullable=False)
    media_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)

    # Type de disponibilité (pour cette plateforme spécifique)
    availability_type: Mapped[str] = mapped_column(
        String(20),
        nullable=False  # stream, rent, buy
    )

    # Pays (code ISO 2 lettres)
    country: Mapped[str] = mapped_column(String(2), nullable=False, index=True)

    # Prix
    price: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2), nullable=True)
    currency: Mapped[Optional[str]] = mapped_column(String(3), nullable=True)  # USD, EUR, etc.

    # Qualité
    quality: Mapped[Optional[str]] = mapped_column(
        String(10),
        nullable=True  # SD, HD, 4K
    )

    # Dates de disponibilité
    available_from: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    available_until: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    # URL directe
    link_url: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)

    # Actif
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Dernière vérification
    last_verified: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    __table_args__ = (
        UniqueConstraint(
            "platform_id", "media_type", "media_id", "availability_type", "country",
            name="uq_availability"
        ),
        CheckConstraint(
            "media_type IN ('movie', 'series')",
            name="check_availability_media_type"
        ),
        CheckConstraint(
            "availability_type IN ('stream', 'rent', 'buy')",
            name="check_availability_type"
        ),
        CheckConstraint(
            "quality IN ('SD', 'HD', '4K', NULL)",
            name="check_quality"
        ),
        Index("idx_availability_lookup", "media_type", "media_id", "country"),
        Index("idx_availability_platform", "platform_id", "country", "is_active"),
    )

    def __repr__(self) -> str:
        return (
            f"Availability(platform_id={self.platform_id}, media_type={self.media_type}, "
            f"media_id={self.media_id}, type={self.availability_type}, country={self.country})"
        )
