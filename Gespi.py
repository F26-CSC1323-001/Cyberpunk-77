"""
Swipe your hand over the APDS-9960 sensor:
    swipe RIGHT = next song
    swipe LEFT  = previous song
    swipe UP    = pause
    swipe DOWN  = play
"""

import time

import board
import busio
from adafruit_apds9960.apds9960 import APDS9960

from music_player import MusicPlayer


# Reads the APDS-9960 sensor and tells a MusicPlayer what to do.
class GestureControl:

    # the numbers the sensor library gives us for each gesture
    UP = 1
    DOWN = 2
    LEFT = 3
    RIGHT = 4

    COOLDOWN = 1.0  # seconds to ignore gestures after one is used

    def __init__(self, player, flip_left_right=False):
        self.player = player
        self.flip_left_right = flip_left_right  # set True if left/right feel backwards
        self.last_time = 0

        i2c = busio.I2C(board.SCL, board.SDA)
        self.sensor = APDS9960(i2c)
        self.sensor.enable_proximity = True
        self.sensor.enable_gesture = True

    """Ask the sensor for a gesture. Returns a number (1-4) or 0 if nothing."""
    def read_gesture(self):
        return self.sensor.gesture()

    """Run the right MusicPlayer method for this gesture."""
    def handle_gesture(self, gesture):
        if self.flip_left_right:
            if gesture == self.LEFT:
                gesture = self.RIGHT
            elif gesture == self.RIGHT:
                gesture = self.LEFT

        if gesture == self.RIGHT:
            print("Swipe right -> next")
            self.player.next_song()
        elif gesture == self.LEFT:
            print("Swipe left -> previous")
            self.player.previous_song()
        elif gesture == self.UP:
            print("Swipe up -> pause")
            self.player.pause()
        elif gesture == self.DOWN:
            print("Swipe down -> play")
            self.player.play()

    # Keep checking the sensor forever
    def run(self):
        print("Gesture ready - swipe over the sensor (Ctrl+C to quit)")

        while True:
            gesture = self.read_gesture()

            if gesture != 0:
                # cooldown so one swipe can't trigger twice
                if time.time() - self.last_time > self.COOLDOWN:
                    self.handle_gesture(gesture)
                    self.last_time = time.time()

            time.sleep(0.05)


if __name__ == "__main__":
    player = MusicPlayer()  # make a MusicPlayer object
    gestures = GestureControl(player)  # make a GestureControl object that uses it
    try:
        gestures.run()
    except KeyboardInterrupt:
        print("Bye!")