"""
music_player.py

The MusicPlayer class is the ONLY place that actually changes the music.
Both gesture_control.py and voice_control.py create a MusicPlayer object
and call its methods (next_song, previous_song, pause, play).

Windows setup:   pip install pyautogui
Pi setup:        sudo apt install playerctl
"""

import platform
import subprocess


class MusicPlayer:
    """Sends commands to whatever music app is playing (Spotify, etc.)."""

    def __init__(self):
        # Attribute: True if this computer is Windows, False if it's the Pi
        self.is_windows = platform.system() == "Windows"

        # Attribute: on Windows, each action is a keyboard media key.
        # Windows only has one play/pause key, so pause and play share it.
        self.windows_keys = {
            "next": "nexttrack",
            "previous": "prevtrack",
            "pause": "playpause",
            "play": "playpause",
        }

    # ---------- Methods you can call from other files ----------

    def next_song(self):
        self._send("next")

    def previous_song(self):
        self._send("previous")

    def pause(self):
        self._send("pause")

    def play(self):
        self._send("play")

    # ---------- Private method (the underscore means "internal use") ----------

    def _send(self, action):
        """action is one of: next, previous, pause, play"""
        print(">>", action)
        try:
            if self.is_windows:
                import pyautogui

                pyautogui.press(self.windows_keys[action])
            else:
                subprocess.run(["playerctl", action])
        except Exception as error:
            print("Error:", error)
