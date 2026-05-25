"""Clock — cycle-accurate timing for the hardware simulator."""


class Clock:
    """System clock driving all CPU and bus timing.

    Tracks cycles, frequency, and provides tick/advance for
    cycle-accurate simulation.
    """

    def __init__(self, frequency_hz=1_000_000):
        self.cycle = 0
        self.frequency_hz = frequency_hz
        self._running = False

    @property
    def period_ns(self):
        return 1_000_000_000 / self.frequency_hz

    def tick(self):
        self.cycle += 1
        return self.cycle

    def advance(self, n=1):
        for _ in range(n):
            self.tick()
        return self.cycle

    def reset(self):
        self.cycle = 0
        self._running = False

    def start(self):
        self._running = True

    def stop(self):
        self._running = False

    @property
    def time_us(self):
        return (self.cycle / self.frequency_hz) * 1_000_000

    @property
    def time_ms(self):
        return (self.cycle / self.frequency_hz) * 1_000

    def stats(self):
        return {
            "cycle": self.cycle,
            "freq_hz": self.frequency_hz,
            "running": self._running,
        }
