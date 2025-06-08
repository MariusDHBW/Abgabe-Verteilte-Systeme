from typing import Optional, List
from pydantic import BaseModel, EmailStr, validator
from datetime import datetime

# ========================
# ==== USER SCHEMAS ======
# ========================


class UserBase(BaseModel):
    username: str
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None

    @validator("email", "full_name", pre=True)
    def empty_string_to_none(cls, v):
        if v == "":
            return None
        return v


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int
    disabled: Optional[bool] = False

    class Config:
        from_attributes = True


# ========================
# ==== TOKEN SCHEMAS =====
# ========================


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


# ========================
# ==== VIDEO SCHEMAS =====
# =======================


class VideoCreate(BaseModel):
    youtube_video_id: Optional[str]
    title: str
    created_at: datetime


class Video(BaseModel):
    id: int
    youtube_video_id: str
    title: str
    created_at: datetime

    users: Optional[List[User]] = []
    download_url: Optional[str] = None
    thumbnail_url: Optional[str] = None

    class Config:
        from_attributes = True


# ==========================
# ==== PLAYLIST SCHEMAS ====
# ==========================


class PlaylistBase(BaseModel):
    title: str
    youtube_playlist_id: Optional[str] = None  # NEU: externe YouTube Playlist ID


class PlaylistCreate(PlaylistBase):
    user_id: int
    created_at: Optional[datetime] = None
    video_ids: Optional[List[int]] = []


class Playlist(PlaylistBase):
    id: int
    created_at: datetime
    user: list[User] = []
    videos: List[Video] = []

    class Config:
        from_attributes = True


# ============================
# ==== DOWNLOAD SCHEMAS ======
# =============================


class PlaylistDownload(BaseModel):
    url: str


# Optional: falls du mit Pydantic v2 arbeitest
User.model_rebuild()
Video.model_rebuild()
Playlist.model_rebuild()
