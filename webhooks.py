from __future__ import annotations

from datetime import date, datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class Message(BaseModel):
    message: str


class UserCreate(BaseModel):
    email: EmailStr
    display_name: str = Field(min_length=2, max_length=120)
    password: str = Field(min_length=12, max_length=200)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class PasswordRequest(BaseModel):
    email: EmailStr


class PasswordReset(BaseModel):
    token: str
    password: str = Field(min_length=12, max_length=200)


class VerifyEmail(BaseModel):
    token: str


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    email: EmailStr
    display_name: str
    role: str
    tier: str
    is_verified: bool
    is_active: bool
    created_at: datetime


class AuthResponse(BaseModel):
    user: UserOut
    csrf_token: str


class CheckoutRequest(BaseModel):
    plan: Literal["pro", "elite"]


class CheckoutResponse(BaseModel):
    url: str


class SettingUpdate(BaseModel):
    values: dict[str, Any]


class AdminOperationRequest(BaseModel):
    force_official: bool = False


class PickOut(BaseModel):
    id: str
    game_id: str
    card_date: date
    matchup: str
    commence_time: datetime
    market: str
    selection: str
    line: float | None
    bookmaker: str
    price: int
    model_probability: float
    market_probability: float
    fair_odds: int
    edge: float
    expected_value: float
    confidence: float
    data_quality: int
    score: float
    grade: str
    units: float
    is_official: bool
    result: str | None
    profit_units: float | None
    clv: float | None
    reasons: list[str]


class DashboardResponse(BaseModel):
    as_of: datetime
    tier: str
    record: dict[str, Any]
    official: list[PickOut]
    watchlist: list[PickOut]
    games: list[dict[str, Any]]


class PerformanceResponse(BaseModel):
    summary: dict[str, Any]
    daily: list[dict[str, Any]]
    by_market: list[dict[str, Any]]
    by_grade: list[dict[str, Any]]
