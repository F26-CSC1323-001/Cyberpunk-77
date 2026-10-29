"""
Say:
    "change" / "next" / "skip"  = next song
    "back" / "previous"         = previous song
    "pause" / "stop"            = pause
    "play" / "resume"           = play

"""

import speech_recognition as sr

from music_player import MusicPlayer

#Listens to the microphone and tells a MusicPlayer what to do.
class VoiceControl:
    

    #the words used for each command
    NEXT_WORDS = ("change", "next", "skip")
    PREVIOUS_WORDS = ("back", "previous")
    PAUSE_WORDS = ("pause", "stop")
    PLAY_WORDS = ("play", "resume")

    #the MusicPlayer we control, plus the speech tools
    def __init__(self, player):
        self.player = player
        self.recognizer = sr.Recognizer()
        self.mic = sr.Microphone()  # uses your default microphone

    def calibrate(self):
        with self.mic as source:
            print("Calibrating for background noise...")
            self.recognizer.adjust_for_ambient_noise(source, duration=1)


    """Listen for one short phrase. Returns the text, or None if its not  clear."""
    def listen(self):
        with self.mic as source:
            try:
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=3)
            except sr.WaitTimeoutError:
                return None  

        try:
            return self.recognizer.recognize_google(audio).lower()
        except sr.UnknownValueError:
            return None  
        except sr.RequestError as error:
            print("Speech service error:", error)
            return None

    """Look for a command word in the text and runs the right method."""
    def handle_text(self, text):
        for word in text.split():
            if word in self.NEXT_WORDS:
                self.player.next_song()
                return
            elif word in self.PREVIOUS_WORDS:
                self.player.previous_song()
                return
            elif word in self.PAUSE_WORDS:
                self.player.pause()
                return
            elif word in self.PLAY_WORDS:
                self.player.play()
                return

    # Auto relistens Keep listening forever"
    def run(self):
        self.calibrate()
        print("Voice ready - say change, pause or play (Ctrl+C to quit)")

        while True:
            text = self.listen()
            if text:
                print("Heard:", text)
                self.handle_text(text)


if __name__ == "__main__":
    player = MusicPlayer()  # make a MusicPlayer object
    voice = VoiceControl(player)  # make a VoiceControl object that uses it
    try:
        voice.run()
    except KeyboardInterrupt:
        print("Bye!")
