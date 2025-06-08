# Youtube-Video-Downloader

## Übersicht

Willkommen zu unserem Projekt! Diese Anwendung ist ein YouTube-Downloader, der auf einer FastAPI-Backend-Architektur basiert und mit einem HTML-Frontend verbunden ist. Unsere Lösung ermöglicht es Nutzern, YouTube-Videos und -Playlists herunterzuladen.

## Installation

1. **Repository klonen:**

   ```bash
   git clone https://github.com/docdschan/VerteilteSysteme.git
   ```
2. **Abhängigkeiten installieren:**
   Wir verwenden Docker, für unsere Datenbank und phpmyadmin. Stellen Sie sicher, dass Docker auf Ihrem System installiert ist.

   ```bash
   docker-compose up --build
   ```
3. **Datenbank einrichten:**
   Unsere Anwendung verwendet eine MariaDB-Datenbank. Diese wird automatisch mit Docker initialisiert. Sie müssen keine weiteren Schritte ausführen.
4. **Requirements.txt**
   venv erstellen mit der requirements.txt

   ```bash
   pip install -r requirements.txt
   ```
5. **FastAPI starten**

   ```bash
   uvicorn fastapi_test.main:app --reload
   ```
6. **Frontend**
   Frontend muss über einen Lokalen-Server gehostet werden. In vs code eignet sich die Erweiterung Live Server.

## Entwickler

- **Jan Lau:** Datenbankstrukturierung und -einrichtung.
- **Marius Lüdtke:** Implementierung der Login- und Registrierungsfunktionen.
- **Jan Schneeberg:** Entwicklung der Download-Logik und Projektmanagement.
