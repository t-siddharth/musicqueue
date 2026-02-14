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

    def log_message(self, format, *args):
        # Suppress server logs
        pass


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
        scope = "user-read-playback-state user-modify-playback-state user-read-email user-read-private"

        auth_url = (
            f"{self.AUTH_URL}?client_id={self.client_id}"
            f"&response_type=code"
            f"&redirect_uri={self.redirect_uri}"
            f"&scope={scope}"
        )

        server = HTTPServer(("localhost", 8888), CallbackHandler)
        threading.Thread(target=server.handle_request).start()

        print("\n🔐 Opening Spotify authorization page...")
        print("Please log in to your Spotify account and authorize the app.")
        webbrowser.open(auth_url)

        print("Waiting for authorization...")
        timeout = 120  # 2 minutes timeout
        start_time = time.time()
        
        while CallbackHandler.auth_code is None:
            if time.time() - start_time > timeout:
                server.server_close()
                raise TimeoutError("Authorization timed out. Please try again.")
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
        print("✓ Authorization successful!\n")

    # -------------------------
    # TEST LOGIN STATUS
    # -------------------------

    def test_login_status(self):
        """
        Test if user is properly logged in and authenticated
        Returns: dict with status information
        """
        print("\n🔍 Testing Spotify login status...")
        
        if not self.access_token:
            return {
                "logged_in": False,
                "error": "No access token available. Need to authenticate first."
            }
        
        try:
            # Test 1: Get current user profile
            response = requests.get(
                f"{self.API_BASE}/me",
                headers={"Authorization": f"Bearer {self.access_token}"},
            )
            
            if response.status_code == 401:
                return {
                    "logged_in": False,
                    "error": "Access token is invalid or expired."
                }
            
            response.raise_for_status()
            user_info = response.json()
            
            print(f"✓ Logged in as: {user_info.get('display_name', 'Unknown')}")
            print(f"  Email: {user_info.get('email', 'N/A')}")
            print(f"  Account type: {user_info.get('product', 'free').upper()}")
            
            # Test 2: Check if user has Premium (required for playback control)
            has_premium = user_info.get('product', 'free') == 'premium'
            
            if not has_premium:
                return {
                    "logged_in": True,
                    "user_info": user_info,
                    "has_premium": False,
                    "warning": "Spotify Premium is required to control playback via API."
                }
            
            # Test 3: Check for available devices
            devices_response = requests.get(
                f"{self.API_BASE}/me/player/devices",
                headers={"Authorization": f"Bearer {self.access_token}"},
            )
            
            devices_response.raise_for_status()
            devices = devices_response.json()["devices"]
            
            print(f"  Active devices: {len(devices)}")
            
            if devices:
                for device in devices:
                    status = "🟢 ACTIVE" if device.get('is_active') else "⚪ Inactive"
                    print(f"    {status} - {device['name']} ({device['type']})")
            
            return {
                "logged_in": True,
                "user_info": user_info,
                "has_premium": True,
                "devices": devices,
                "device_count": len(devices)
            }
            
        except requests.exceptions.HTTPError as e:
            return {
                "logged_in": False,
                "error": f"HTTP Error: {e.response.status_code} - {e.response.text}"
            }
        except Exception as e:
            return {
                "logged_in": False,
                "error": f"Error testing login: {str(e)}"
            }

    # -------------------------
    # VERIFY PREREQUISITES
    # -------------------------

    def verify_prerequisites(self):
        """
        Verify all prerequisites are met before attempting playback
        Returns: True if ready, False otherwise
        """
        print("\n" + "=" * 50)
        print("VERIFYING PREREQUISITES")
        print("=" * 50)
        
        # Step 1: Check login status
        status = self.test_login_status()
        
        if not status["logged_in"]:
            print(f"\n❌ Not logged in: {status.get('error', 'Unknown error')}")
            return False
        
        print("\n✓ Login verified")
        
        # Step 2: Check for Premium
        if not status.get("has_premium", False):
            print("\n⚠️  WARNING: You have a FREE Spotify account")
            print("   Spotify Premium is required to control playback via API.")
            print("\n   Options:")
            print("   1. Upgrade to Spotify Premium")
            print("   2. Use the 'Open in Spotify app' method instead")
            return False
        
        print("✓ Premium account confirmed")
        
        # Step 3: Check for devices
        if status.get("device_count", 0) == 0:
            print("\n⚠️  No active Spotify devices found!")
            print("\n   To fix this:")
            print("   1. Open Spotify desktop app (or mobile app)")
            print("   2. Play ANY song (you can pause it right after)")
            print("   3. Wait 5-10 seconds for the device to register")
            
            retry = input("\n   Have you done this? (y/n): ").lower()
            
            if retry == 'y':
                print("\n   Checking again...")
                time.sleep(2)
                status = self.test_login_status()
                
                if status.get("device_count", 0) == 0:
                    print("\n   ❌ Still no devices found")
                    return False
                else:
                    print(f"\n   ✓ Found {status['device_count']} device(s)!")
            else:
                return False
        else:
            print(f"✓ Found {status['device_count']} active device(s)")
        
        print("\n" + "=" * 50)
        print("✓ ALL PREREQUISITES MET - Ready to play!")
        print("=" * 50 + "\n")
        
        return True

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
            return None

        # Prefer active device, otherwise use first available
        for device in devices:
            if device.get('is_active'):
                return device["id"]
        
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

        if response.status_code == 204:
            return True
        elif response.status_code == 403:
            print("\n⚠️  Error: Premium account required for playback control")
            return False
        else:
            print(f"\n⚠️  Playback error: {response.status_code}")
            if response.text:
                print(f"   Details: {response.text}")
            return False

    # -------------------------
    # OPEN IN SPOTIFY APP
    # -------------------------

    def open_in_spotify_app(self, playlist_uri):
        """Alternative: Open playlist directly in Spotify app using spotify:// URI"""
        # Convert spotify:playlist:xxx to spotify://playlist/xxx
        spotify_url = playlist_uri.replace(":", "/").replace("spotify/", "spotify://")
        print(f"\n🎵 Opening in Spotify app...")
        webbrowser.open(spotify_url)
        return True

    # -------------------------
    # MAIN LOGIC
    # -------------------------

    def play_adhd_focus_music(self):
        # Step 1: Authenticate
        self.authenticate()
        
        # Step 2: Verify prerequisites (login, premium, devices)
        prerequisites_met = self.verify_prerequisites()
        
        # Step 3: Choose music
        print("\nChoose music type:")
        print("1. Lofi Beats Focus")
        print("2. Study Music")
        print("3. Custom Search")

        choice = input("\nEnter choice: ")

        if choice == "1":
            query = "lofi beats focus"
        elif choice == "2":
            query = "study music concentration"
        elif choice == "3":
            query = input("Enter search term: ")
        else:
            print("Invalid choice.")
            return False

        print(f"\n🔍 Searching for: {query}")
        playlists = self.search_playlist(query)

        if not playlists:
            print("No playlists found.")
            return False

        print("\nSelect playlist:")
        for i, playlist in enumerate(playlists):
            print(f"{i+1}. {playlist['name']} by {playlist['owner']['display_name']}")

        try:
            selection = int(input("\nEnter number: ")) - 1
        except ValueError:
            print("Invalid selection.")
            return False

        if selection < 0 or selection >= len(playlists):
            print("Invalid selection.")
            return False

        selected_playlist = playlists[selection]

        # Step 4: Play music (method depends on prerequisites)
        if prerequisites_met:
            # Use API playback control
            device_id = self.get_active_device()
            if not device_id:
                print("\n⚠️  No device found. Opening in Spotify app instead...")
                return self.open_in_spotify_app(selected_playlist["uri"])

            print(f"\n🎵 Starting playback on your device...")
            success = self.start_playback(device_id, selected_playlist["uri"])

            if success:
                print("✓ Playback started successfully!")
                return True
            else:
                print("\nFalling back to opening in Spotify app...")
                return self.open_in_spotify_app(selected_playlist["uri"])
        else:
            # Fallback: Open in Spotify app
            print("\n💡 Using fallback method: Opening in Spotify app")
            return self.open_in_spotify_app(selected_playlist["uri"])


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

    print("=" * 50)
    print("🎵 Spotify Focus Music Player")
    print("=" * 50)

    player = SpotifyPlayer(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        redirect_uri=REDIRECT_URI
    )

    try:
        player.play_adhd_focus_music()
    except KeyboardInterrupt:
        print("\n\nExiting...")
    except Exception as e:
        print(f"\n❌ Error: {e}")