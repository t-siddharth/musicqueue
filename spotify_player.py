import os
import subprocess
from pathlib import Path


# =========================
# LOCAL MUSIC PLAYER
# =========================

class LocalMusicPlayer:
    def __init__(self, music_directory=None):
        self.music_directory = music_directory or self.find_music_directory()

    # -------------------------
    # FIND MUSIC DIRECTORY
    # -------------------------

    def find_music_directory(self):
        """Use ayola's Music directory only"""
        music_dir = Path("C:/Users/ayola/Music")
        if music_dir.exists():
            return str(music_dir)
        else:
            print(f"⚠️  Warning: {music_dir} not found!")
            return str(music_dir)

    # -------------------------
    # SCAN ALL AUDIO FILES
    # -------------------------

    def scan_all_audio_files(self):
        """Scan for all audio files in the music directory and subdirectories"""
        search_dir = Path(self.music_directory)
        
        if not search_dir.exists():
            print(f"❌ Directory not found: {search_dir}")
            return []
        
        # All supported audio formats
        audio_extensions = ['.mp3', '.wav', '.flac', '.m4a', '.aac', '.wma', '.ogg', '.opus', '.mp4', '.m4b']
        
        music_files = []
        print(f"\n🔍 Scanning: {search_dir}")
        
        for ext in audio_extensions:
            found_files = list(search_dir.glob(f'**/*{ext}'))
            music_files.extend(found_files)
        
        return sorted(music_files)

    # -------------------------
    # PLAY ALL FILES
    # -------------------------

    def play_all(self):
        """Find and play all audio files"""
        print("=" * 60)
        print("🎵 Local Music Player")
        print("=" * 60)
        print(f"\n📁 Music directory: {self.music_directory}")
        
        # Scan for all audio files
        music_files = self.scan_all_audio_files()
        
        if not music_files:
            print("\n⚠️  No audio files found!")
            print(f"\nTo add music, place audio files in:")
            print(f"   {self.music_directory}")
            print("\nSupported formats: MP3, WAV, FLAC, M4A, AAC, WMA, OGG, OPUS")
            return False
        
        print(f"\n✓ Found {len(music_files)} audio files")
        
        # Show first 10 files as preview
        print("\n📋 Files found (showing first 10):")
        for i, file_path in enumerate(music_files[:10]):
            print(f"   • {file_path.name}")
        
        if len(music_files) > 10:
            print(f"   ... and {len(music_files) - 10} more")
        
        # Play all files
        print(f"\n🎵 Playing all {len(music_files)} files...")
        
        try:
            if os.name == 'nt':  # Windows
                # On Windows, add all files to default media player queue
                for file_path in music_files:
                    os.startfile(str(file_path))
            else:  # macOS/Linux
                for file_path in music_files:
                    subprocess.Popen(['xdg-open', str(file_path)])
            
            print("✓ Music started playing in your default media player!")
            print("\n💡 Tip: Use your media player controls to:")
            print("   - Skip tracks")
            print("   - Shuffle")
            print("   - Adjust volume")
            return True
            
        except Exception as e:
            print(f"\n❌ Error playing files: {e}")
            return False


# =========================
# RUN
# =========================

if __name__ == "__main__":
    # You can set a custom directory here or it will use your Music folder
    MUSIC_DIR = os.getenv("MUSIC_DIRECTORY", None)
    
    player = LocalMusicPlayer(music_directory=MUSIC_DIR)
    
    try:
        player.play_all()
    except KeyboardInterrupt:
        print("\n\nExiting...")
    except Exception as e:
        print(f"\n❌ Error: {e}")