import streamlit as st
import spotipy
import re
import os
from dotenv import load_dotenv
from spotipy.oauth2 import SpotifyClientCredentials
from fpdf import FPDF
from io import BytesIO
import logging
import random
from fpdf.enums import XPos, YPos

load_dotenv()

SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")


sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
    client_id=SPOTIFY_CLIENT_ID,
    client_secret=SPOTIFY_CLIENT_SECRET
))

# --- LOGGING CONFIGURATION ---
logging.basicConfig(
    level=logging.ERROR,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# --- ERROR HANDLING ---
def handle_error(error: Exception, user_message: str = None) -> str:
    """Handle errors gracefully and log them appropriately."""
    error_id = random.randint(1000, 9999)
    logger.error(f"Error ID {error_id}: {str(error)}", exc_info=True)
    if user_message:
        return f"{user_message} (Error ID: {error_id})"
    return f"An unexpected error occurred. Please try again later. (Error ID: {error_id})"

def extract_spotify_id(url: str) -> str:
    match = re.search(r"(album|track)[/|:]([a-zA-Z0-9]+)", url)
    return match.group(2) if match else None

def fetch_metadata(spotify_url: str) -> dict:
    if "album" in spotify_url:
        album_id = extract_spotify_id(spotify_url)
        album = sp.album(album_id)
        return {
            "type": "album",
            "album_name": album["name"],
            "release_date": album["release_date"],
            "label": album["label"],
            "tracks": [{
                "track_number": track["track_number"],
                "title": track["name"],
                "isrc": track["external_ids"]["isrc"]
            } for track in album["tracks"]["items"]]
        }
    elif "track" in spotify_url:
        track_id = extract_spotify_id(spotify_url)
        track = sp.track(track_id)
        return {
            "type": "track",
            "title": track["name"],
            "release_date": track["album"]["release_date"],
            "label": sp.album(track["album"]["id"])["label"],
            "isrc": track["external_ids"]["isrc"]
        }
    else:
        raise ValueError("Invalid Spotify URL")

def generate_pdf_bytes(metadata: dict) -> BytesIO:
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("helvetica", size=12)

    if metadata["type"] == "album":
        pdf.cell(200, 10, f"Album: {metadata['album_name']}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.cell(200, 10, f"Release Date: {metadata['release_date']}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.cell(200, 10, f"Label: {metadata['label']}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.cell(200, 10, "Tracklist & ISRCs:", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

        for track in metadata["tracks"]:
            pdf.cell(200, 10, f"{track['track_number']}. {track['title']} - {track['isrc']}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    else:
        pdf.cell(200, 10, f"Track: {metadata['title']}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.cell(200, 10, f"Release Date: {metadata['release_date']}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.cell(200, 10, f"Label: {metadata['label']}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.cell(200, 10, f"ISRC: {metadata['isrc']}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    buffer = BytesIO()
    pdf.output(buffer)
    buffer.seek(0)
    return buffer

# --- CONFIGURATION ---
try:
    st.set_page_config(page_title="Spotify Metadata Scraper", layout="wide")
    st.image("https://cdn.prod.website-files.com/60951ede1223b809acdb2eee/67e9b49e3df19ee8404a180b_MTL_logo_horizontal_2.svg", width=200)
except Exception as e:
    logger.error("Failed to set page config", exc_info=True)

# Custom CSS
st.markdown("""
<style>
    .stButton > button {
        background-color: #c6f222 !important;
        border: none !important;
        border-radius: 0 !important;
        color: black !important;
    }
    .stTextInput input {
        border-radius: 0 !important;
    }
    .stRadio > label {
        color: black !important;
    }
    .stRadio > div[role="radiogroup"] > label > div:first-child {
        background-color: #c6f222 !important;
        border-color: #c6f222 !important;
    }
    .stRadio > div[role="radiogroup"] > label > div:first-child > div {
        background-color: black !important;
        border-color: black !important;
    }
    div[data-testid="stHorizontalBlock"] > div:nth-child(2) {
        display: flex;
        align-items: flex-end;
        padding-bottom: 10px;
    }
    div[data-testid="stImage"] {
        margin-bottom: 2rem;
    }
</style>
""", unsafe_allow_html=True)

# --- LAYOUT ---
left_col, right_col = st.columns([1, 1])

with left_col:
    st.title("🎵 Spotify Metadata Scraper")
    st.markdown("""
    Paste a link to an album or track to download metadata (ISRC, label, date, tracklist).<br>
    <span style='color: #888;'>e.g: https://open.spotify.com/track/7HKez549fwJQDzx3zLjHKC?si=127e706087124590</span>
    """, unsafe_allow_html=True)
    url = st.text_input("🔗 Paste a Spotify link (album or track)")
    if url:
        try:
            metadata = fetch_metadata(url)
            st.success("Metadata read successfully!")
            if metadata["type"] == "album":
                st.subheader(metadata["album_name"])
                st.write(f"📅 Release date: {metadata['release_date']}")
                st.write(f"🏷️ Label: {metadata['label']}")
                st.write("🎶 Tracklist:")
                for track in metadata["tracks"]:
                    st.markdown(f"- {track['track_number']}. **{track['title']}** — *{track['isrc']}*")
            else:
                st.subheader(metadata["title"])
                st.write(f"📅 Release date: {metadata['release_date']}")
                st.write(f"🏷️ Label: {metadata['label']}")
                st.write(f"💿 ISRC: {metadata['isrc']}")
            pdf_bytes = generate_pdf_bytes(metadata)
            st.download_button(
                label="📄 Download PDF with metadata",
                data=pdf_bytes,
                file_name="spotify_metadata.pdf",
                mime="application/pdf"
            )
        except Exception as e:
            error_message = handle_error(e, "We encountered an issue while processing your request. Our team has been notified.")
            st.error(error_message)
            if not os.getenv("PRODUCTION", False):
                st.exception(e)  # Only show full error in development

with right_col:
    st.markdown("""
    <div style="border: 2px solid #c6f222; padding: 24px; border-radius: 10px;">
        <h3 class="text-lg font-bold text-gray-900 mb-4">About Spotify Metadata</h3>
        <p class="text-gray-600 mb-4">Spotify Metadata is a tool that allows you to download metadata (ISRC, label, date, tracklist) from a Spotify album or track.</p>
        <h3 class="text-lg font-bold text-gray-900 mb-2">Helpful Links</h3>
        <ul class="text-blue-600 underline mb-8">
            <li><a href="https://developer.spotify.com/dashboard" target="_blank">Spotify Developer Dashboard</a></li>
            <li><a href="https://developer.spotify.com/documentation/web-api/reference" target="_blank">Spotify API Reference</a></li>
        </ul>
        <h3 class="text-lg font-bold text-gray-900 mb-2">MusicTech Lab's ❤️ Coding</h3>
        <ul class="text-blue-600 underline mb-8">
            <li><a href="https://www.musictechlab.io" target="_blank">MusicTechLab's Website</a></li>
            <li><a href="https://github.com/musictechlab/mtl-scrapmeup" target="_blank">GitHub link for this project</a></li>
            <li><a href="https://www.linkedin.com/company/musictechlab/" target="_blank">MusicTech Lab's LinkedIn</a></li>
            <li><a href="https://resources.musictechlab.io" target="_blank">MTL Resources - All MusicTech Resources in One Place</a></li>
            <li><a href="mailto:office@musictechlab.io">Wants to implement Spotify Metadata? Contact Us 🤘</a></li>
        </ul>
        <div style="margin-top: 2rem;">
            <h3 class="text-lg font-bold text-gray-900 mb-4">How to Use This Tool</h3>
            <p class="text-gray-600">You can either paste track or album link and click the download button.</p>
        </div>
                <div>
                <image src="https://i.ytimg.com/vi/SGyOaCXr8Lw/maxresdefault.jpg" width=350>
                </div>
    </div>
    """, unsafe_allow_html=True)