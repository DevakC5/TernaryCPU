import time
import threading


class Audio:
    def __init__(self):
        self._enabled = False
        self._notes = []

    def play_beep(self, frequency=440, duration=0.1):
        if not self._enabled:
            return
        self._notes.append((frequency, duration))

    def play_tone(self, frequency, duration):
        self.play_beep(frequency, duration)

    def enable(self):
        self._enabled = True

    def disable(self):
        self._enabled = False

    def clear(self):
        self._notes.clear()


audio = Audio()
