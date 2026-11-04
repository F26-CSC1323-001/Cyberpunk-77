
import platform
import subprocess


class MusicPlayer:
    """Sends commands to whatever music app is playing eg (Spotify)."""

    def __init__(self):
        self.is_windows = platform.system() == "Windows"
        self.windows_keys = {
            "next": "nexttrack",
            "previous": "prevtrack",
            "pause": "playpause",
            "play": "playpause",
        }

    # -------------Methods you can call from other files------------

    def next_song(self):
        self._send("next")

    def previous_song(self):
        self._send("previous")

    def pause(self):
        self._send("pause")

    def play(self):
        self._send("play")

    # -------------Private method-----------------

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
