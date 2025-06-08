from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Table
from sqlalchemy.orm import relationship
from .database import Base

# Assoziationstabelle: Nutzer ↔ Videos (viele-zu-viele)
user_videos = Table(
    "user_videos",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id"), primary_key=True),
    Column("video_id", Integer, ForeignKey("videos.id"), primary_key=True),
)

# Assoziationstabelle: Playlists ↔ Videos (viele-zu-viele)
playlist_videos = Table(
    "playlist_videos",
    Base.metadata,
    Column("playlist_id", Integer, ForeignKey("playlists.id"), primary_key=True),
    Column("video_id", Integer, ForeignKey("videos.id"), primary_key=True),
)

user_playlist_association = Table(
    "user_playlists",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id"), primary_key=True),
    Column("playlist_id", Integer, ForeignKey("playlists.id"), primary_key=True),
)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(120), unique=True, index=True, nullable=True)
    full_name = Column(String(100), nullable=True)
    hashed_password = Column(String(128), nullable=False)
    disabled = Column(Boolean, default=False)

    videos = relationship("Video", secondary=user_videos, back_populates="users")
    playlists = relationship(
        "Playlist", secondary=user_playlist_association, back_populates="users"
    )


class Video(Base):
    __tablename__ = "videos"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    youtube_video_id = Column(String(255), unique=True, index=True)
    title = Column(String(255), nullable=False)
    created_at = Column(DateTime, nullable=False)

    users = relationship("User", secondary=user_videos, back_populates="videos")
    playlists = relationship(
        "Playlist", secondary=playlist_videos, back_populates="videos"
    )


class Playlist(Base):
    __tablename__ = "playlists"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    youtube_playlist_id = Column(String(255), unique=True, index=True, nullable=False)
    title = Column(String(255), nullable=False)
    created_at = Column(DateTime, nullable=False)

    videos = relationship(
        "Video", secondary=playlist_videos, back_populates="playlists"
    )
    users = relationship(
        "User", secondary=user_playlist_association, back_populates="playlists"
    )
