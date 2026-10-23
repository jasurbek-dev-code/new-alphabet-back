from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field


class TelegramUserData(BaseModel):
    id: int = Field(..., description="Telegram User ID")
    first_name: str = Field(..., description="User's first name")
    last_name: Optional[str] = Field(None, description="User's last name")
    username: Optional[str] = Field(None, description="Telegram username without @")
    language_code: Optional[str] = Field(None, description="IETF language tag")
    is_premium: Optional[bool] = Field(None, description="True if user is Telegram Premium")
    allows_write_to_pm: Optional[bool] = Field(None, description="True if user allowed bot to message them")


class AuthRequest(BaseModel):
    init_data: str = Field(
        ...,
        description="The raw initData query string received from Telegram.WebApp.initData",
        alias="initData",
    )

    model_config = ConfigDict(populate_by_name=True)


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    telegram_id: int
    first_name: str
    last_name: Optional[str] = None
    username: Optional[str] = None
    language_code: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class AuthResponse(BaseModel):
    user: UserResponse
    is_new_user: bool = Field(
        ..., description="Indicates if the user was just registered or updated"
    )
    auth_date: datetime = Field(
        ..., description="Timestamp when Telegram validated this session"
    )


# --- Translation & History Schemas ---

class TranslationRequest(BaseModel):
    text: str = Field(
        ...,
        min_length=1,
        max_length=50000,
        description="Original Uzbek Latin text to be transliterated",
    )


class TranslationResponse(BaseModel):
    id: int = Field(..., description="Unique ID of the translation record")
    original_text: str
    translated_text: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TranslationHistoryItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    original_text: str
    translated_text: str
    created_at: datetime


class TranslationHistoryListResponse(BaseModel):
    total: int = Field(..., description="Total count of translation history items")
    page: int = Field(..., description="Current page number")
    per_page: int = Field(..., description="Items per page")
    items: List[TranslationHistoryItem]

