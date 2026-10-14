
import queue
import threading
import tkinter as tk

from music_player import MusicPlayer

# Voice control
try:
    from vc_control import VoiceControl

    VOICE_AVAILABLE = True
except ImportError:
    VOICE_AVAILABLE = False


class MusicGUI:
    def __init__(self, root):
        self.root = root
        self.player = MusicPlayer()

        # Voice control pieces
        self.voice = None
        self.voice_thread = None
        self.stop_voice = threading.Event()
        self.messages = queue.Queue()  

        # window
        root.title("Music Player")
        root.geometry("360x260")
        root.resizable(False, False)

        tk.Label(root, text="Music Player", font=("Arial", 18, "bold")).pack(pady=(15, 5))

        self.status = tk.StringVar(value="Ready")
        tk.Label(root, textvariable=self.status, font=("Arial", 11)).pack(pady=2)

        #music buttons
        row = tk.Frame(root)
        row.pack(pady=15)

        buttons = [
            ("Previous", self.player.previous_song),
            ("Play", self.player.play),
            ("Pause", self.player.pause),
            ("Next", self.player.next_song),
        ]
        for text, action in buttons:
            tk.Button(
                row,
                text=text,
                width=7,
                height=2,
                command=lambda t=text, a=action: self.press(t, a),
            ).pack(side="left", padx=4)

        # ---------------- voice control ----------------
        self.voice_button = tk.Button(
            root, text="Voice control: OFF", width=22, command=self.toggle_voice
        )
        self.voice_button.pack(pady=5)
        if not VOICE_AVAILABLE:
            self.voice_button.config(state="disabled", text="Voice control unavailable")

        self.heard = tk.StringVar(value="")
        tk.Label(root, textvariable=self.heard, font=("Arial", 10, "italic")).pack(pady=5)

        # Keyboard shortcuts
        root.bind("<Left>", lambda e: self.press("Previous", self.player.previous_song))
        root.bind("<Right>", lambda e: self.press("Next", self.player.next_song))
        root.bind("<space>", lambda e: self.press("Play/Pause", self.player.play))

        root.protocol("WM_DELETE_WINDOW", self.close)
        self.check_messages()

    #button actions

    def press(self, name, action):
        """Run a MusicPlayer method and show what happened."""
        action()
        self.status.set(f"Sent: {name}")

    #voice control

    def toggle_voice(self):
        if self.voice_thread and self.voice_thread.is_alive():
            # Turn it off
            self.stop_voice.set()
            self.voice_button.config(state="disabled", text="Stopping...")
            return

        try:
            while True:
                kind, value = self.messages.get_nowait()
                if kind == "status":
                    self.status.set(value)
                elif kind == "heard":
                    self.voice_button.config(state="normal", text="Voice control: OFF")
    def close(self):


    root.mainloop()
if __name__ == "__main__":
    root = tk.Tk()
    MusicGUI(root)
        self.stop_voice.set()
        self.root.destroy()
                    self.status.set("Voice control off")
        except queue.Empty:
            pass
        self.root.after(100, self.check_messages)

                    self.heard.set(f'Heard: "{value}"')
                elif kind == "voice_stopped":

        so only the main thread is allowed to change the window)."""
    def check_messages(self):
        """Check for updates from the voice thread (tkinter isn't thread-safe,
        finally:
            self.messages.put(("voice_stopped", ""))
                    self.voice.handle_text(text)
        except Exception as error:
            self.messages.put(("status", f"Voice error: {error}"))
            while not self.stop_voice.is_set():
                    self.messages.put(("heard", text))
                text = self.voice.listen()
                if text:

            self.messages.put(("status", "Listening: next, back, pause, play"))

    def voice_worker(self):
            self.voice.calibrate()
        try:
            self.messages.put(("status", "Calibrating mic..."))
        # Turn it on
        self.voice_button.config(text="Voice control: ON")

        self.voice_thread.start()
        self.stop_voice.clear()
        self.voice_thread = threading.Thread(target=self.voice_worker, daemon=True)
        if self.voice is None:
            try:

