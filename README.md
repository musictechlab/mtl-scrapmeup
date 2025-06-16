# MTL ScrapMeUp 🎵

Spotify Metadata Scraper built with Streamlit and Python 🐍. Paste a link to any Spotify album or track and get:

- ✅ ISRC codes  
- ✅ Label information  
- ✅ Release date  
- ✅ Full tracklist  
- ✅ Export to PDF

## 🚀 How to run

### With Poetry (locally)

1. Clone this repo  
2. Create `.env` with your Spotify credentials  
3. Run the app:

```bash
poetry install
poetry run streamlit run mtl_scrapmeup.py
```

Please add to your .env file:
```
SPOTIFY_CLIENT_ID=your_client_id
SPOTIFY_CLIENT_SECRET=your_client_secret
```

---

### With Docker

1. Clone this repo
2. Create a `.env` file in the project root with your Spotify credentials:
   ```
   SPOTIFY_CLIENT_ID=your_client_id
   SPOTIFY_CLIENT_SECRET=your_client_secret
   ```
3. Build and run the app with Docker Compose:
   ```bash
   docker compose up --build
   ```
4. Visit [http://localhost:8501](http://localhost:8501) in your browser.

The `.env` file will be used to pass your Spotify credentials to the container. The Streamlit configuration can be customized in the `.streamlit` directory if needed.
