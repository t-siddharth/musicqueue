"""
Example usage of the SpotifyPlayer class

These examples show different ways to use the Spotify focus music player.
"""

import os
from spotify_player import SpotifyPlayer


# Example 1: Simple interactive mode
def example_interactive():
    """Run the interactive focus music player."""
    player = SpotifyPlayer()
    player.play_adhd_focus_music()


# Example 2: Search for a specific playlist
def example_search_playlist():
    """Search for a specific playlist and show results."""
    player = SpotifyPlayer()
    
    query = "lofi beats"
    print(f"Searching for playlists: {query}")
    
    playlists = player.search_playlist(query)
    
    for i, playlist in enumerate(playlists, 1):
        print(f"{i}. {playlist['name']}")
        print(f"   Owner: {playlist['owner']['display_name']}")
        print(f"   Tracks: {playlist['tracks']['total']}")
        print()


# Example 3: Search for specific tracks
def example_search_tracks():
    """Search for specific tracks."""
    player = SpotifyPlayer()
    
    query = "lo-fi hip hop"
    print(f"Searching for tracks: {query}")
    
    tracks = player.search_track(query)
    
    for i, track in enumerate(tracks, 1):
        artists = ", ".join([artist['name'] for artist in track['artists']])
        print(f"{i}. {track['name']} by {artists}")


# Example 4: Play a specific track
def example_play_specific_track():
    """Play a specific track by URI."""
    player = SpotifyPlayer()
    
    # Example track URI - you'd get this from search results
    track_uri = "spotify:track:11dFghVXANMlKmJXsNCQvb"  # Example: Lo-Fi Beats
    
    print(f"Playing track: {track_uri}")
    player.start_playback(uris=[track_uri])


# Example 5: Integrate with focus detection
def example_focus_integration():
    """
    Example of integrating with the focus detection from focus_background.py
    
    This would play focus music when a focus app is detected.
    """
    from focus_background import get_active_window_info
    
    focus_keywords = ['vscode', 'visualstudio', 'sublime', 'notepad', 'python', 'code']
    
    title, process = get_active_window_info()
    
    if process and any(keyword in process.lower() for keyword in focus_keywords):
        print(f"Focus app detected: {process}")
        print("Starting focus music...")
        
        player = SpotifyPlayer()
        # Play lofi beats
        playlists = player.search_playlist("lofi beats focus")
        if playlists:
            player.start_playback(context_uri=playlists[0]['uri'])


# Example 6: Get available devices
def example_list_devices():
    """List all available Spotify devices."""
    player = SpotifyPlayer()
    
    devices = player.get_devices()
    
    if devices:
        print("Available Spotify Devices:")
        for i, device in enumerate(devices, 1):
            print(f"{i}. {device['name']} ({device['type']})")
    else:
        print("No Spotify devices found. Make sure Spotify is running.")


if __name__ == "__main__":
    import sys
    
    print("Spotify Focus Music Player - Examples\n")
    print("1. Interactive Mode (Recommended)")
    print("2. Search Playlists")
    print("3. Search Tracks")
    print("4. List Devices")
    
    choice = input("\nChoose an example (1-4): ").strip()
    
    try:
        if choice == '1':
            example_interactive()
        elif choice == '2':
            example_search_playlist()
        elif choice == '3':
            example_search_tracks()
        elif choice == '4':
            example_list_devices()
        else:
            print("Invalid choice")
    except Exception as e:
        print(f"Error: {e}")
        print("\nMake sure you have set your Spotify credentials:")
        print("  set SPOTIFY_CLIENT_ID=your_id")
        print("  set SPOTIFY_CLIENT_SECRET=your_secret")
