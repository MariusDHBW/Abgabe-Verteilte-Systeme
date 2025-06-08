import os
import yt_dlp

from fastapi_test import database


def get_metadata(link: str) -> dict:
    database.logger.info(f"Metadaten werden abgerufen für: {link}")
    ydl_opts = {
        "quiet": True,
        "no_warnings": True,
        "cookiefile": "fastapi_test/cookies.txt",
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        metadata = ydl.extract_info(link, download=False)
        database.logger.debug(
            f"Metadaten empfangen: {metadata.get('title', 'Kein Titel')}"
        )
        return metadata


def download_video(link: str, *, file_extension: str = "mp4") -> dict:
    database.logger.info(f"Download gestartet für Video: {link}")

    try:
        metadata = get_metadata(link)
        video_id = metadata["id"]
        title = metadata.get("title", "unknown_title")
        database.logger.info(f"Video-Infos: ID={video_id}, Titel='{title}'")
    except Exception as e:
        database.logger.error(f"Fehler beim Abrufen der Metadaten: {e}")
        raise RuntimeError(f"Fehler beim Abrufen der Metadaten: {e}")

    ydl_opts = {
        "format": "best",
        "outtmpl": "videos/%(id)s.%(ext)s",
        "cookiefile": "fastapi_test/cookies.txt",
        "quiet": True,
        "no_warnings": True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([link])
            database.logger.info(f"Video erfolgreich heruntergeladen: {video_id}")
    except Exception as e:
        database.logger.exception("Fehler beim Video-Download")
        raise RuntimeError(f"Fehler beim Video-Download: {e}")

    return {
        "youtube_video_id": video_id,
        "title": title,
    }


def download_playlist(playlist_url: str, *, file_extension: str = "mp4") -> dict:
    database.logger.info(f"Download gestartet für Playlist: {playlist_url}")
    os.makedirs("videos", exist_ok=True)

    try:
        playlist_metadata = get_metadata(playlist_url)
    except Exception as e:
        database.logger.error(f"Fehler beim Abrufen der Playlist-Metadaten: {e}")
        raise RuntimeError(f"Fehler beim Abrufen der Playlist-Metadaten: {e}")

    playlist_id = playlist_metadata.get("id", "unknown_playlist")
    playlist_title = playlist_metadata.get("title", "unknown_playlist_title")
    entries = playlist_metadata.get("entries", [])
    database.logger.info(f"Playlist-ID: {playlist_id}, Videos gefunden: {len(entries)}")

    ydl_opts = {
        "format": "best",
        "outtmpl": "videos/%(id)s.%(ext)s",
        "cookiefile": "fastapi_test/cookies.txt",
        "yes_playlist": True,
        "quiet": True,
        "no_warnings": True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([playlist_url])
            database.logger.info(f"Playlist erfolgreich heruntergeladen: {playlist_id}")
    except Exception as e:
        database.logger.exception("Fehler beim Playlist-Download")
        raise RuntimeError(f"Fehler beim Playlist-Download: {e}")

    downloaded_files = []
    for entry in entries:
        video_id = entry.get("id")
        title = entry.get("title", "unknown")
        database.logger.debug(f"Video aus Playlist: ID={video_id}, Titel='{title}'")
        downloaded_files.append(
            {
                "youtube_video_id": video_id,
                "title": title,
            }
        )

    return {
        "playlist_id": playlist_id,
        "title": playlist_title,
        "videos": downloaded_files,
    }
