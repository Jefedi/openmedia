"""Modèle de base SQLAlchemy"""
from datetime import datetime
from typing import Any

from sqlalchemy import Column, DateTime, Integer
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Classe de base pour tous les modèles"""

    # Générer automatiquement le nom de la table depuis le nom de la classe
    @declared_attr.directive
    def __tablename__(cls) -> str:
        """Générer le nom de table en snake_case"""
        import re
        name = cls.__name__
        # Convertir CamelCase en snake_case
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

    # Colonnes communes à tous les modèles
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    def dict(self) -> dict[str, Any]:
        """Convertir le modèle en dictionnaire"""
        return {
            column.name: getattr(self, column.name)
            for column in self.__table__.columns
        }

    def __repr__(self) -> str:
        """Représentation string du modèle"""
        attrs = ", ".join(
            f"{k}={v!r}"
            for k, v in self.dict().items()
            if k not in ("created_at", "updated_at")
        )
        return f"{self.__class__.__name__}({attrs})"
