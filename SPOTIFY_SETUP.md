# Spotify Focus Music Player - Setup Guide

## Quick Start

### 1. Get Spotify API Credentials
- Go to https://developer.spotify.com/dashboard
- Sign in or create a Spotify Developer Account (free)
- Click "Create an App" and accept the terms
- You'll get a **Client ID** and **Client Secret**
- Note: You need a Spotify account (free or premium, but playback requires premium)

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Set Environment Variables
**On Windows (Command Prompt):**
```cmd
set SPOTIFY_CLIENT_ID=your_client_id_here
set SPOTIFY_CLIENT_SECRET=your_client_secret_here
```

**On Windows (PowerShell):**
```powershell
$env:SPOTIFY_CLIENT_ID='your_client_id_here'
$env:SPOTIFY_CLIENT_SECRET='your_client_secret_here'
```

**On Windows (Permanent - Set System Environment Variables):**
1. Search for "Environment Variables" in Windows
2. Click "Edit the system environment variables"
3. Click "Environment Variables"
4. Add new User variables:
   - Variable name: `SPOTIFY_CLIENT_ID`
   - Variable value: `your_client_id_here`
   - Variable name: `SPOTIFY_CLIENT_SECRET`
   - Variable value: `your_client_secret_here`

### 4. Run the Program
```bash
python spotify_player.py
```

## Features
- 🎵 Search for playlists and tracks
- 📋 Pre-set focus music options (lofi, ambient, study, video game)
- 🔍 Custom search capability
- 🎯 Easy-to-use interactive menu
- ✓ ADHD-friendly UI (simple numbered choices)

## Music Recommendations for ADHD Focus
- **Lofi Beats**: Great for concentration, less distracting
- **Ambient Focus**: Minimal, calming background
- **Video Game Music**: Familiar patterns help some with focus
- **Study Music**: Specifically curated for productivity

## Troubleshooting

### "Authentication failed"
- Check your Client ID and Client Secret are correct
- Make sure environment variables are set properly
- Restart your terminal after setting environment variables

### "No devices available"
- Ensure Spotify is running on at least one device
- Only Spotify Premium accounts can use the playback API

### "Search failed"
- Check your internet connection
- Verify Spotify API is accessible

## Advanced: Using with focus_background.py

You can integrate this with the existing `focus_background.py` to automatically play music when you switch to a focus app:

```python
from spotify_player import SpotifyPlayer

def play_focus_music_on_app_focus():
    """Automatically play focus music when switching to a focus app"""
    player = SpotifyPlayer()
    player.play_adhd_focus_music()
```

## References
- Spotify Web API Docs: https://developer.spotify.com/documentation/web-api
- Spotipy Library: https://spotipy.readthedocs.io/
