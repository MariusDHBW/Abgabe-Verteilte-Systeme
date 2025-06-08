import os
import logging
import shutil
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from .config import settings

# === Logging Setup ===
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# === Pfade und DB Setup ===
VIDEOS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "videos"))

engine = create_engine(
    settings.SQLALCHEMY_DATABASE_URL,
    pool_pre_ping=True,
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# === Datenbank-Session ===
def get_db():
    db = SessionLocal()
    try:
        yield db
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


# === Video-Ordner bereinigen ===
def clear_videos_folder():
    """Löscht den gesamten 'videos'-Ordner und erstellt ihn neu."""
    if os.path.exists(VIDEOS_DIR):
        try:
            shutil.rmtree(VIDEOS_DIR)
            logger.info(f"Ordner '{VIDEOS_DIR}' wurde komplett gelöscht.")
        except Exception as e:
            logger.error(f"Fehler beim Löschen des Ordners '{VIDEOS_DIR}': {e}")

    # Ordner neu erstellen
    try:
        os.makedirs(VIDEOS_DIR, exist_ok=True)
        logger.info(f"Ordner '{VIDEOS_DIR}' wurde neu erstellt.")
    except Exception as e:
        logger.error(f"Fehler beim Erstellen des Ordners '{VIDEOS_DIR}': {e}")


# === Initialisierung ===
def init_db():
    """Initialisiert die Datenbank und bereitet die Verzeichnisse vor."""
    if settings.DEBUG:
        logger.info(
            "DEBUG-Modus aktiviert: Tabellen und Inhalte der Download-Ordner werden gelöscht."
        )
        Base.metadata.drop_all(bind=engine)
        clear_videos_folder()

    Base.metadata.create_all(bind=engine)
