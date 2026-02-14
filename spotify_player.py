import os
import base64
import requests
import webbrowser
import threading
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs
from dotenv import load_dotenv


# =========================
# CALLBACK HANDLER
# =========================

class CallbackHandler(BaseHTTPRequestHandler):
    auth_code = None

    def do_GET(self):
        query = parse_qs(urlparse(self.path).query)
        if "code" in query:
            CallbackHandler.auth_code = query["code"][0]
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"Authorization successful. You can close this window.")
        else:
            self.send_response(400)
            self.end_headers()


# =========================
# SPOTIFY PLAYER
# =========================

class SpotifyPlayer:
    AUTH_URL = "https://accounts.spotify.com/authorize"
    TOKEN_URL = "https://accounts.spotify.com/api/token"
    API_BASE = "https://api.spotify.com/v1"

    def __init__(self, client_id, client_secret, redirect_uri):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.access_token = None

    # -------------------------
    # AUTHENTICATION
    # -------------------------

    def authenticate(self):
        scope = "user-read-playback-state user-modify-playback-state"

        auth_url = (
            f"{self.AUTH_URL}?client_id={self.client_id}"
            f"&response_type=code"
            f"&redirect_uri={self.redirect_uri}"
            f"&scope={scope}"
        )

        server = HTTPServer(("localhost", 8888), CallbackHandler)
        threading.Thread(target=server.handle_request).start()

        webbrowser.open(auth_url)

        print("Waiting for Spotify authorization...")
        while CallbackHandler.auth_code is None:
            time.sleep(1)

        server.server_close()

        auth_header = base64.b64encode(
            f"{self.client_id}:{self.client_secret}".encode()
        ).decode()

        response = requests.post(
            self.TOKEN_URL,
            headers={
                "Authorization": f"Basic {auth_header}",
                "Content-Type": "application/x-www-form-urlencoded",
            },
            data={
                "grant_type": "authorization_code",
                "code": CallbackHandler.auth_code,
                "redirect_uri": self.redirect_uri,
            },
        )

        response.raise_for_status()
        self.access_token = response.json()["access_token"]

    # -------------------------
    # GET DEVICE
    # -------------------------

    def get_active_device(self):
        response = requests.get(
            f"{self.API_BASE}/me/player/devices",
            headers={"Authorization": f"Bearer {self.access_token}"},
        )

        response.raise_for_status()
        devices = response.json()["devices"]

        if not devices:
            print("No active Spotify devices found. Open Spotify app first.")
            return None

        return devices[0]["id"]

    # -------------------------
    # SEARCH PLAYLIST
    # -------------------------

    def search_playlist(self, query):
        response = requests.get(
            f"{self.API_BASE}/search",
            headers={"Authorization": f"Bearer {self.access_token}"},
            params={
                "q": query,
                "type": "playlist",
                "limit": 5,
            },
        )

        response.raise_for_status()
        return response.json()["playlists"]["items"]

    # -------------------------
    # START PLAYBACK
    # -------------------------

    def start_playback(self, device_id, playlist_uri):
        response = requests.put(
            f"{self.API_BASE}/me/player/play",
            headers={"Authorization": f"Bearer {self.access_token}"},
            params={"device_id": device_id},
            json={"context_uri": playlist_uri},
        )

        return response.status_code == 204

    # -------------------------
    # MAIN LOGIC
    # -------------------------

    def play_adhd_focus_music(self):
        self.authenticate()

        print("\nChoose music type:")
        print("1. Lofi Beats Focus")

        choice = input("Enter choice: ")

        if choice != "1":
            print("Invalid choice.")
            return False

        playlists = self.search_playlist("lofi beats focus")

        if not playlists:
            print("No playlists found.")
            return False

        print("\nSelect playlist:")
        for i, playlist in enumerate(playlists):
            print(f"{i+1}. {playlist['name']} by {playlist['owner']['display_name']}")

        selection = int(input("Enter number: ")) - 1

        if selection < 0 or selection >= len(playlists):
            print("Invalid selection.")
            return False

        selected_playlist = playlists[selection]

        device_id = self.get_active_device()
        if not device_id:
            return False

        success = self.start_playback(device_id, selected_playlist["uri"])

        if success:
            print("Playback started successfully!")
            return True
        else:
            print("Playback failed.")
            return False


# =========================
# RUN
# =========================

if __name__ == "__main__":
    load_dotenv()

    CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
    CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
    REDIRECT_URI = os.getenv("SPOTIFY_REDIRECT_URI", "http://localhost:8888/callback")

    if not CLIENT_ID or not CLIENT_SECRET:
        raise ValueError("Missing Spotify credentials in .env file")

    player = SpotifyPlayer(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        redirect_uri=REDIRECT_URI
    )

    player.play_adhd_focus_music()
