# MTL ScrapMeUp 🎵

Spotify Metadata Scraper built with Streamlit and Python 🐍. Paste a link to any Spotify album or track and get:

- ✅ ISRC codes  
- ✅ Label information  
- ✅ Release date  
- ✅ Full tracklist  
- ✅ Export to PDF

## 🚀 How to run

1. Clone this repo  
2. Create `.env` with your Spotify credentials  
3. Run the app:

```bash
poetry install
poetry run streamlit run mtl_scrapmeup.py

Please add to your .env file
SPOTIFY_CLIENT_ID=your_client_id
SPOTIFY_CLIENT_SECRET=your_client_secret# mtl-scrapmeup
