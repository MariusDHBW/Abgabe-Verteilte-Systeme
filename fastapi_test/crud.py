import os
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from fastapi import HTTPException
from datetime import datetime
from sqlalchemy import delete

from . import models, schemas, database

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# =============================
# User Management
# =============================


def get_user_by_username(db: Session, username: str):
    database.logger.debug(f"Suche Benutzer mit Username: {username}")
    return db.query(models.User).filter(models.User.username == username).first()


def create_user(db: Session, user_in: schemas.UserCreate):
    database.logger.info(f"Erstelle neuen Benutzer: {user_in.username}")
    hashed_pw = pwd_context.hash(user_in.password)
    db_user = models.User(
        username=user_in.username,
        email=user_in.email,
        full_name=user_in.full_name,
        hashed_password=hashed_pw,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    database.logger.info(f"Benutzer erfolgreich erstellt: {user_in.username}")
    return db_user


def authenticate_user(db: Session, username: str, password: str):
    database.logger.debug(f"Authentifiziere Benutzer: {username}")
    user = get_user_by_username(db, username)
    if not user:
        database.logger.warning(f"Benutzer nicht gefunden: {username}")
        return None
    if not pwd_context.verify(password, user.hashed_password):
        database.logger.warning(f"Falsches Passwort für Benutzer: {username}")
        return None
    database.logger.info(f"Benutzer erfolgreich authentifiziert: {username}")
    return user


def change_user_password(
    db: Session, user_id: int, old_password: str, new_password: str
):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Benutzer nicht gefunden")

    if not pwd_context.verify(old_password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Altes Passwort ist falsch")

    user.hashed_password = pwd_context.hash(new_password)
    db.commit()
    return user


# =============================
# Video Management
# =============================


def create_video(db: Session, video: schemas.VideoCreate, user_id: int):
    database.logger.info(f"Füge Video hinzu für Benutzer-ID {user_id}: {video.title}")
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        database.logger.error("Benutzer nicht gefunden")
        raise HTTPException(status_code=404, detail="Benutzer nicht gefunden")

    existing_video = (
        db.query(models.Video)
        .filter(models.Video.youtube_video_id == video.youtube_video_id)
        .first()
    )

    if existing_video:
        database.logger.debug(f"Video existiert bereits: {video.youtube_video_id}")
        if existing_video not in user.videos:
            user.videos.append(existing_video)
            db.commit()
            db.refresh(existing_video)
        return existing_video

    db_video = models.Video(
        youtube_video_id=video.youtube_video_id,
        title=video.title,
        created_at=video.created_at,
    )
    db.add(db_video)

    user.videos.append(db_video)

    db.commit()
    db.refresh(db_video)
    database.logger.info(f"Video erfolgreich gespeichert: {video.title}")
    return db_video


def get_user_videos(db: Session, user_id: int):
    database.logger.debug(f"Rufe Videos ab für Benutzer-ID: {user_id}")
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user:
        return user.videos
    database.logger.warning(
        f"Benutzer nicht gefunden beim Abrufen von Videos: {user_id}"
    )
    return []


def delete_video_for_user(db: Session, user_id: int, video_id: int):
    # 1. Entferne user-video Zuordnung aus der Association Table
    stmt = delete(models.user_videos).where(
        models.user_videos.c.user_id == user_id,
        models.user_videos.c.video_id == video_id,
    )
    result = db.execute(stmt)
    if result.rowcount == 0:
        raise Exception("Video gehört nicht zum Nutzer oder existiert nicht")

    db.commit()

    # 2. Prüfe, ob das Video noch weiteren Nutzern gehört
    remaining_users = (
        db.query(models.user_videos)
        .filter(models.user_videos.c.video_id == video_id)
        .count()
    )

    if remaining_users == 0:
        # 3. Video-Eintrag löschen
        video = db.query(models.Video).filter(models.Video.id == video_id).first()
        if video:
            video_path = os.path.join("videos", f"{video.youtube_video_id}.mp4")
            db.delete(video)
            db.commit()

            # 4. Datei löschen (optional)
            try:
                if video_path and os.path.exists(video_path):
                    os.remove(video_path)
            except Exception as e:
                print(f"Fehler beim Löschen der Datei: {e}")


# =============================
# Playlist Management
# =============================


def create_playlist(db: Session, playlist_in: schemas.PlaylistCreate):
    database.logger.info(f"Erstelle Playlist für Benutzer-ID: {playlist_in.user_id}")
    user = db.query(models.User).filter(models.User.id == playlist_in.user_id).first()
    if not user:
        database.logger.error("Benutzer nicht gefunden beim Erstellen der Playlist")
        raise HTTPException(status_code=404, detail="Benutzer nicht gefunden")

    existing_playlist = (
        db.query(models.Playlist)
        .filter(models.Playlist.youtube_playlist_id == playlist_in.youtube_playlist_id)
        .first()
    )

    if existing_playlist:
        database.logger.debug(
            f"Playlist existiert bereits: {playlist_in.youtube_playlist_id}"
        )
        if existing_playlist not in user.playlists:
            user.playlists.append(existing_playlist)
            db.commit()
            db.refresh(existing_playlist)
        return existing_playlist

    playlist = models.Playlist(
        title=playlist_in.title,
        created_at=playlist_in.created_at or datetime.utcnow(),
        youtube_playlist_id=playlist_in.youtube_playlist_id,
    )

    if playlist_in.video_ids:
        videos = (
            db.query(models.Video)
            .filter(models.Video.id.in_(playlist_in.video_ids))
            .all()
        )
        playlist.videos = videos

    playlist.users.append(user)

    db.add(playlist)
    db.commit()
    db.refresh(playlist)
    database.logger.info(f"Playlist erfolgreich erstellt: {playlist.title}")
    return playlist
