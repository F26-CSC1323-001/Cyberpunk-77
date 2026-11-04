"""
gesture_control.py  (needs music_player.py in the same folder)

    swipe RIGHT = next song
    swipe LEFT  = previous song
    swipe UP    = pause
    swipe DOWN  = play

On the Raspberry Pi: reads the real APDS-9960 sensor.
On Windows: there is no sensor, so it runs in TEST MODE where you type
right / left / up / down and press Enter to pretend you swiped.

Pi setup:   sudo raspi-config -> Interface Options -> I2C -> Enable (reboot)
            sudo i2cdetect -y 1        (you should see 39)
            pip install adafruit-circuitpython-apds9960
"""

import platform
import time

from music_player import MusicPlayer


class GestureControl:
    """Reads swipes and tells a MusicPlayer what to do."""

    # Class constants: the numbers the sensor gives us for each swipe.
    # If a swipe does the wrong thing on the Pi, swap these numbers.
    UP = 1
    DOWN = 2
    LEFT = 3
    RIGHT = 4

    def __init__(self, player):
        # Attribute: the MusicPlayer object we give commands to
        self.player = player

    def handle_gesture(self, gesture):
        """Take a gesture number and call the right MusicPlayer method."""
        if gesture == self.RIGHT:
            self.player.next_song()
        elif gesture == self.LEFT:
            self.player.previous_song()
        elif gesture == self.UP:
            self.player.pause()
        elif gesture == self.DOWN:
            self.player.play()

    def run_sensor(self):
        """Read the real APDS-9960 sensor (Raspberry Pi)."""
        import board
        from adafruit_apds9960.apds9960 import APDS9960

        i2c = board.I2C()
        sensor = APDS9960(i2c)
        sensor.enable_proximity = True
        sensor.enable_gesture = True
        print("Gesture sensor ready - swipe your hand (Ctrl+C to quit)")

        while True:
            gesture = sensor.gesture()  # 0 means no gesture yet
            if gesture != 0:
                print("Gesture:", gesture)
                self.handle_gesture(gesture)
                time.sleep(1)  # so one swipe isn't counted twice
            time.sleep(0.05)

    def run_test(self):
        """Pretend swipes by typing, for testing without the sensor (Windows)."""
        names = {
            "right": self.RIGHT,
            "left": self.LEFT,
            "up": self.UP,
            "down": self.DOWN,
        }
        print("TEST MODE (no sensor). Type right, left, up or down, then Enter.")
        print("Press Ctrl+C to quit.")

        while True:
            text = input("swipe> ").strip().lower()
            if text in names:
                self.handle_gesture(names[text])
            else:
                print("Type one of: right, left, up, down")

    def run(self):
        """Pick test mode on Windows, the real sensor on the Pi."""
        if platform.system() == "Windows":
            self.run_test()
        else:
            self.run_sensor()


if __name__ == "__main__":
    player = MusicPlayer()  # make a MusicPlayer object
    gestures = GestureControl(player)  # make a GestureControl object that uses it
    try:
        gestures.run()
    except KeyboardInterrupt:
        print("Bye!")
