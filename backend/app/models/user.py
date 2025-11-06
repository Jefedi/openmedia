"""Modèles liés aux utilisateurs et à l'authentification"""
from datetime import datetime
from typing import Optional
import secrets

from sqlalchemy import Boolean, String, Integer, DateTime, Text, JSON, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class User(Base):
    """Modèle utilisateur"""

    __tablename__ = "users"

    # Informations de base
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)

    # Profil
    full_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    avatar_url: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    bio: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Statut
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Dates
    last_login: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    email_verified_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Sécurité
    failed_login_attempts: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    locked_until: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Préférences
    preferences: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True, default=dict)

    # Synchronisation externe
    trakt_token: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    trakt_refresh_token: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    trakt_expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Relations
    api_keys: Mapped[list["APIKey"]] = relationship(
        "APIKey",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    refresh_tokens: Mapped[list["RefreshToken"]] = relationship(
        "RefreshToken",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"User(id={self.id}, email={self.email}, username={self.username})"


class APIKey(Base):
    """Clés API pour accès programmatique"""

    __tablename__ = "api_keys"

    # Relations
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    user: Mapped["User"] = relationship("User", back_populates="api_keys")

    # Clé
    key_hash: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    prefix: Mapped[str] = mapped_column(String(10), nullable=False)  # Pour identifier la clé

    # Permissions et limites
    scopes: Mapped[list] = mapped_column(JSON, nullable=False, default=list)  # ['read', 'write', 'admin']
    rate_limit_per_hour: Mapped[int] = mapped_column(Integer, default=100, nullable=False)
    rate_limit_per_day: Mapped[int] = mapped_column(Integer, default=2000, nullable=False)

    # Statut
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    last_used: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Usage tracking
    total_requests: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    @staticmethod
    def generate_key() -> tuple[str, str, str]:
        """
        Générer une nouvelle clé API

        Returns:
            (clé complète, hash, prefix)
        """
        # Générer une clé aléatoire
        key = secrets.token_urlsafe(32)
        prefix = key[:8]

        # En production, utiliser un hash sécurisé
        from passlib.context import CryptContext
        pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")
        key_hash = pwd_context.hash(key)

        return key, key_hash, prefix

    def __repr__(self) -> str:
        return f"APIKey(id={self.id}, name={self.name}, prefix={self.prefix})"


class RefreshToken(Base):
    """Tokens de rafraîchissement JWT"""

    __tablename__ = "refresh_tokens"

    # Relations
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    user: Mapped["User"] = relationship("User", back_populates="refresh_tokens")

    # Token
    token_hash: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    jti: Mapped[str] = mapped_column(String(36), unique=True, index=True, nullable=False)  # JWT ID

    # Métadonnées
    device_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    user_agent: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    ip_address: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)  # IPv6 max length

    # Statut
    is_revoked: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    last_used: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    def __repr__(self) -> str:
        return f"RefreshToken(id={self.id}, jti={self.jti}, user_id={self.user_id})"
