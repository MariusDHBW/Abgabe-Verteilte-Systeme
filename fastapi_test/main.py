import os
import httpx
from datetime import timedelta, datetime
from fastapi import FastAPI, Depends, HTTPException, status, Form, Query
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from fastapi_test import schemas, crud, database, deps, config
from fastapi_test.youtube_downloader import download_video, download_playlist

app = FastAPI()

# =============================
# App Setup
# =============================

app.add_event_handler("startup", database.init_db)

os.makedirs("videos", exist_ok=True)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
media_path = os.path.abspath(os.path.join(BASE_DIR, "..", "videos"))
app.mount("/videos", StaticFiles(directory=media_path), name="videos")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =============================
# Auth
# =============================


@app.post("/token", response_model=schemas.Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db=Depends(database.get_db),
):
    user = crud.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        database.logger.warning(
            f"Login fehlgeschlagen für Benutzer: {form_data.username}"
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )

    access_token_expires = timedelta(
        minutes=config.settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    access_token = deps.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    database.logger.info(f"Token erstellt für Benutzer: {user.username}")
    return {"access_token": access_token, "token_type": "bearer"}


# =============================
# Benutzer
# =============================


@app.post("/register", response_model=schemas.User)
async def register(
    username: str = Form(...),
    password: str = Form(...),
    password_repeat: str = Form(...),
    email: str = Form(None),
    full_name: str = Form(None),
    db=Depends(database.get_db),
):
    if password != password_repeat:
        database.logger.warning("Passwörter stimmen nicht überein bei Registrierung")
        raise HTTPException(status_code=400, detail="Passwörter stimmen nicht überein")

    if crud.get_user_by_username(db, username):
        database.logger.warning(
            f"Registrierung abgelehnt: Benutzername '{username}' bereits vergeben"
        )
        raise HTTPException(status_code=400, detail="Benutzername bereits vergeben")

    database.logger.info(f"Neuer Benutzer registriert: {username}")
    user_in = schemas.UserCreate(
        username=username, password=password, email=email, full_name=full_name
    )
    return crud.create_user(db, user_in)


@app.post("/change-password", response_model=schemas.User)
async def change_password(
    old_password: str = Form(...),
    new_password: str = Form(...),
    current_user: schemas.User = Depends(deps.get_current_active_user),
    db=Depends(database.get_db),
):
    database.logger.info(f"Benutzer {current_user.username} ändert Passwort")
    return crud.change_user_password(
        db,
        user_id=current_user.id,
        old_password=old_password,
        new_password=new_password,
    )


@app.delete("/my-videos/{video_id}")
async def delete_video(
    video_id: int,
    current_user: schemas.User = Depends(deps.get_current_active_user),
    db=Depends(database.get_db),
):
    database.logger.info(f"{current_user.username} löscht Video mit ID: {video_id}")
    return crud.delete_video_for_user(db=db, video_id=video_id, user_id=current_user.id)


# =============================
# Video Download
# =============================


@app.post("/download", response_model=schemas.Video)
async def download_video_for_user(
    link: str = Form(...),
    file_extension: str = Form(None),
    current_user: schemas.User = Depends(deps.get_current_active_user),
    db=Depends(database.get_db),
):
    try:
        video_data_raw = download_video(link, file_extension=file_extension)
        database.logger.info(
            f"Video heruntergeladen: {video_data_raw['title']} ({video_data_raw['youtube_video_id']})"
        )
    except RuntimeError as e:
        database.logger.error(f"Video-Download fehlgeschlagen: {e}")
        raise HTTPException(
            status_code=400, detail=f"Video-Download fehlgeschlagen: {str(e)}"
        )
    except Exception as e:
        database.logger.exception("Unbekannter Fehler beim Video-Download")
        raise HTTPException(status_code=500, detail=f"Interner Serverfehler: {str(e)}")

    video_data = schemas.VideoCreate(
        youtube_video_id=video_data_raw["youtube_video_id"],
        title=video_data_raw["title"],
        created_at=datetime.now(),
    )

    return crud.create_video(db=db, video=video_data, user_id=current_user.id)


# =============================
# Playlist Download
# =============================


@app.post("/download_playlist", response_model=schemas.Playlist)
async def download_playlist_for_user(
    url: str = Form(...),
    file_extension: str = Form(None),
    current_user: schemas.User = Depends(deps.get_current_active_user),
    db=Depends(database.get_db),
):
    try:
        download_result = download_playlist(url, file_extension=file_extension)
        database.logger.info(
            f"Playlist mit {len(download_result['videos'])} Videos erfolgreich heruntergeladen"
        )
    except RuntimeError as e:
        database.logger.error(f"Playlist-Download fehlgeschlagen: {e}")
        raise HTTPException(
            status_code=400, detail=f"Playlist-Download fehlgeschlagen: {str(e)}"
        )
    except Exception as e:
        database.logger.exception("Unbekannter Fehler beim Playlist-Download")
        raise HTTPException(status_code=500, detail=f"Interner Serverfehler: {str(e)}")

    saved_videos = []
    for entry in download_result["videos"]:
        video_data = schemas.VideoCreate(
            youtube_video_id=entry["youtube_video_id"],
            title=entry["title"],
            created_at=datetime.utcnow(),
        )
        saved_video = crud.create_video(
            db=db, video=video_data, user_id=current_user.id
        )
        saved_videos.append(saved_video)

    playlist_in = schemas.PlaylistCreate(
        user_id=current_user.id,
        title=download_result["title"],
        video_ids=[v.id for v in saved_videos],
        created_at=datetime.now(),
        youtube_playlist_id=download_result["playlist_id"],
    )
    return crud.create_playlist(db=db, playlist_in=playlist_in)


# =============================
# User Videos
# =============================


@app.get("/my-videos", response_model=list[schemas.Video])
async def get_my_videos(
    current_user: schemas.User = Depends(deps.get_current_active_user),
    db=Depends(database.get_db),
):
    videos = crud.get_user_videos(db=db, user_id=current_user.id)
    database.logger.info(
        f"{current_user.username} ruft eigene Videos ab ({len(videos)} Treffer)"
    )

    for video in videos:
        video.download_url = (
            f"http://127.0.0.1:8000/videos/{video.youtube_video_id}.mp4"
        )
        video.thumbnail_url = (
            f"https://img.youtube.com/vi/{video.youtube_video_id}/hqdefault.jpg"
        )
    return videos


# =========================
# Pixabay
# =========================

API_KEY_PIXABAY = config.settings.PIXABAY_API_KEY


@app.get("/api/pixabay")
async def pixabay_proxy(q: str = Query(...)):
    url = "https://pixabay.com/api/"
    params = {
        "key": API_KEY_PIXABAY,
        "q": q,
        "image_type": "photo",
        "per_page": 5,
        "page": 1,
        "orientation": "horizontal",
    }
    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params)
        response.raise_for_status()
        return response.json()
