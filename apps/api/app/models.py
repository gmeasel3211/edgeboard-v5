from __future__ import annotations

import uuid
from datetime import date, datetime, timezone
from typing import Any

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    JSON,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .db import Base


def uuid4_str() -> str:
    return str(uuid.uuid4())


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, onupdate=utcnow, nullable=False
    )


class User(TimestampMixin, Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid4_str)
    email: Mapped[str] = mapped_column(String(320), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    display_name: Mapped[str] = mapped_column(String(120), nullable=False)
    role: Mapped[str] = mapped_column(String(30), default="member", index=True, nullable=False)
    tier: Mapped[str] = mapped_column(String(30), default="free", index=True, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    stripe_customer_id: Mapped[str | None] = mapped_column(String(100), unique=True, nullable=True)
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    refresh_tokens: Mapped[list[RefreshToken]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    subscriptions: Mapped[list[Subscription]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid4_str)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    token_hash: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    replaced_by_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)
    user_agent: Mapped[str | None] = mapped_column(String(500), nullable=True)
    ip_address: Mapped[str | None] = mapped_column(String(80), nullable=True)

    user: Mapped[User] = relationship(back_populates="refresh_tokens")


class OneTimeToken(Base):
    __tablename__ = "one_time_tokens"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid4_str)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    purpose: Mapped[str] = mapped_column(String(40), index=True)
    token_hash: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class Subscription(TimestampMixin, Base):
    __tablename__ = "subscriptions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid4_str)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    provider: Mapped[str] = mapped_column(String(30), default="stripe")
    provider_subscription_id: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    provider_customer_id: Mapped[str] = mapped_column(String(120), index=True)
    product_id: Mapped[str | None] = mapped_column(String(120), nullable=True)
    price_id: Mapped[str | None] = mapped_column(String(120), nullable=True)
    tier: Mapped[str] = mapped_column(String(30), default="pro")
    status: Mapped[str] = mapped_column(String(40), index=True)
    current_period_end: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    cancel_at_period_end: Mapped[bool] = mapped_column(Boolean, default=False)

    user: Mapped[User] = relationship(back_populates="subscriptions")


class Game(TimestampMixin, Base):
    __tablename__ = "games"

    id: Mapped[str] = mapped_column(String(150), primary_key=True)
    sport: Mapped[str] = mapped_column(String(20), default="mlb", index=True)
    game_date: Mapped[date] = mapped_column(Date, index=True)
    commence_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    provider_game_id: Mapped[str | None] = mapped_column(String(150), nullable=True, index=True)
    league_game_id: Mapped[str | None] = mapped_column(String(80), nullable=True, index=True)
    away_team: Mapped[str] = mapped_column(String(120), index=True)
    home_team: Mapped[str] = mapped_column(String(120), index=True)
    away_team_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    home_team_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    away_pitcher: Mapped[str | None] = mapped_column(String(120), nullable=True)
    home_pitcher: Mapped[str | None] = mapped_column(String(120), nullable=True)
    away_pitcher_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    home_pitcher_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    venue: Mapped[str | None] = mapped_column(String(150), nullable=True)
    latitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    longitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    status: Mapped[str] = mapped_column(String(40), default="scheduled", index=True)
    away_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    home_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    metadata_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)

    quotes: Mapped[list[Quote]] = relationship(back_populates="game", cascade="all, delete-orphan")
    projections: Mapped[list[Projection]] = relationship(back_populates="game", cascade="all, delete-orphan")
    recommendations: Mapped[list[Recommendation]] = relationship(
        back_populates="game", cascade="all, delete-orphan"
    )

    __table_args__ = (Index("ix_games_sport_date", "sport", "game_date"),)


class Quote(Base):
    __tablename__ = "quotes"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid4_str)
    game_id: Mapped[str] = mapped_column(ForeignKey("games.id", ondelete="CASCADE"), index=True)
    bookmaker: Mapped[str] = mapped_column(String(40), index=True)
    market: Mapped[str] = mapped_column(String(40), index=True)
    selection: Mapped[str] = mapped_column(String(150), index=True)
    line: Mapped[float | None] = mapped_column(Float, nullable=True)
    price: Mapped[int] = mapped_column(Integer)
    implied_probability: Mapped[float] = mapped_column(Float)
    fetched_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)

    game: Mapped[Game] = relationship(back_populates="quotes")

    __table_args__ = (
        Index("ix_quotes_lookup", "game_id", "market", "bookmaker", "fetched_at"),
    )


class Projection(Base):
    __tablename__ = "projections"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid4_str)
    game_id: Mapped[str] = mapped_column(ForeignKey("games.id", ondelete="CASCADE"), index=True)
    model_version: Mapped[str] = mapped_column(String(40), index=True)
    generated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, index=True)
    away_runs: Mapped[float] = mapped_column(Float)
    home_runs: Mapped[float] = mapped_column(Float)
    away_win_probability: Mapped[float] = mapped_column(Float)
    home_win_probability: Mapped[float] = mapped_column(Float)
    total_mean: Mapped[float] = mapped_column(Float)
    data_quality: Mapped[int] = mapped_column(Integer)
    confidence: Mapped[float] = mapped_column(Float)
    market_disagreement: Mapped[float] = mapped_column(Float)
    simulation_count: Mapped[int] = mapped_column(Integer)
    reasons_json: Mapped[list[str]] = mapped_column(JSON, default=list)
    inputs_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    probabilities_json: Mapped[dict[str, float]] = mapped_column(JSON, default=dict)

    game: Mapped[Game] = relationship(back_populates="projections")


class Recommendation(TimestampMixin, Base):
    __tablename__ = "recommendations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid4_str)
    game_id: Mapped[str] = mapped_column(ForeignKey("games.id", ondelete="CASCADE"), index=True)
    projection_id: Mapped[str | None] = mapped_column(ForeignKey("projections.id"), nullable=True)
    card_date: Mapped[date] = mapped_column(Date, index=True)
    market: Mapped[str] = mapped_column(String(40), index=True)
    selection: Mapped[str] = mapped_column(String(150))
    line: Mapped[float | None] = mapped_column(Float, nullable=True)
    bookmaker: Mapped[str] = mapped_column(String(40))
    price: Mapped[int] = mapped_column(Integer)
    model_probability: Mapped[float] = mapped_column(Float)
    market_probability: Mapped[float] = mapped_column(Float)
    fair_odds: Mapped[int] = mapped_column(Integer)
    edge: Mapped[float] = mapped_column(Float)
    expected_value: Mapped[float] = mapped_column(Float)
    confidence: Mapped[float] = mapped_column(Float)
    data_quality: Mapped[int] = mapped_column(Integer)
    score: Mapped[float] = mapped_column(Float)
    grade: Mapped[str] = mapped_column(String(12))
    units: Mapped[float] = mapped_column(Float)
    is_official: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    result: Mapped[str | None] = mapped_column(String(10), nullable=True, index=True)
    profit_units: Mapped[float | None] = mapped_column(Float, nullable=True)
    closing_price: Mapped[int | None] = mapped_column(Integer, nullable=True)
    clv: Mapped[float | None] = mapped_column(Float, nullable=True)
    settled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    reasons_json: Mapped[list[str]] = mapped_column(JSON, default=list)

    game: Mapped[Game] = relationship(back_populates="recommendations")

    __table_args__ = (
        UniqueConstraint(
            "game_id",
            "card_date",
            "market",
            "selection",
            "line",
            "bookmaker",
            name="uq_recommendation_candidate",
        ),
        Index("ix_recommendations_official_date", "is_official", "card_date"),
    )


class AppSetting(TimestampMixin, Base):
    __tablename__ = "app_settings"

    key: Mapped[str] = mapped_column(String(100), primary_key=True)
    value_json: Mapped[Any] = mapped_column(JSON)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    updated_by_user_id: Mapped[str | None] = mapped_column(String(36), nullable=True)


class OperationLog(Base):
    __tablename__ = "operation_logs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid4_str)
    operation: Mapped[str] = mapped_column(String(80), index=True)
    status: Mapped[str] = mapped_column(String(30), index=True)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    triggered_by: Mapped[str] = mapped_column(String(120), default="system")
    summary_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    error_text: Mapped[str | None] = mapped_column(Text, nullable=True)


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid4_str)
    user_id: Mapped[str | None] = mapped_column(String(36), nullable=True, index=True)
    action: Mapped[str] = mapped_column(String(120), index=True)
    entity_type: Mapped[str | None] = mapped_column(String(80), nullable=True)
    entity_id: Mapped[str | None] = mapped_column(String(120), nullable=True)
    ip_address: Mapped[str | None] = mapped_column(String(80), nullable=True)
    metadata_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, index=True)
