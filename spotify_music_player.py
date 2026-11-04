
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent
load_dotenv(PROJECT_DIR / ".env")


class MusicPlayer:

    def __init__(self):
        self.spotify = spotipy.Spotify(
            auth_manager=SpotifyOAuth(
                scope=(
                    "user-modify-playback-state "
                    "user-read-playback-state"
                ),
                cache_path=str(
                    PROJECT_DIR / ".spotify_token_cache"
                )
            )
        )

    def next_song(self):
        self.spotify.next_track()
        print("Next song")

    def previous_song(self):
        self.spotify.previous_track()
        print("Previous song")

    def pause(self):
        self.spotify.pause_playback()
        print("Music paused")

    def play(self):
        self.spotify.start_playback()
        print("Music playing")
