
from spotify_music_player import MusicPlayer

player = MusicPlayer()

print("Testing Spotify...")

while True:
    command = input(
        "n=next, b=previous, p=pause, r=resume, q=quit: "
    ).lower()

    if command == "n":
        player.next_song()
    elif command == "b":
        player.previous_song()
    elif command == "p":
        player.pause()
    elif command == "r":
        player.play()
    elif command == "q":
        break
