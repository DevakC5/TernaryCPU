"""Audio subsystem — PCM mixing and WAV file output."""

import math
import struct
import time
import os


SAMPLE_RATE = 44100
MAX_NOTES = 256
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "..", "audio_output")


class Audio:
    """Simple audio mixer that accumulates notes and writes WAV output.

    Notes are queued per-frame. On ``flush()``, accumulated notes are mixed
    into a PCM buffer and written to a WAV file. Real-time playback is not
    supported; the output can be played with any audio player.
    """

    def __init__(self):
        self._enabled = True
        self._notes = []

    def play_beep(self, frequency=440, duration=0.1):
        """Queue a beep tone.

        Args:
            frequency: Hz (20-20000)
            duration: Seconds
        """
        if not self._enabled:
            return
        if len(self._notes) >= MAX_NOTES:
            return
        self._notes.append((frequency, duration))

    def play_tone(self, frequency, duration):
        """Alias for play_beep."""
        self.play_beep(frequency, duration)

    def enable(self):
        self._enabled = True

    def disable(self):
        self._enabled = False

    def clear(self):
        self._notes.clear()

    def flush(self, filename=None):
        """Mix all queued notes into a WAV file.

        Args:
            filename: Output path (default: audio_output/session_{timestamp}.wav)
        """
        if not self._notes:
            return
        total_samples = 0
        for freq, dur in self._notes:
            total_samples += int(SAMPLE_RATE * dur)

        if total_samples == 0:
            return

        buffer = [0.0] * total_samples
        offset = 0
        for freq, dur in self._notes:
            nsamples = int(SAMPLE_RATE * dur)
            for i in range(nsamples):
                t = i / SAMPLE_RATE
                sample = math.sin(2.0 * math.pi * freq * t)
                buffer[offset + i] += sample * 0.3  # master volume
            offset += nsamples

        # Clamp
        max_val = max(abs(s) for s in buffer) or 1.0
        if max_val > 1.0:
            buffer = [s / max_val for s in buffer]

        if filename is None:
            os.makedirs(OUTPUT_DIR, exist_ok=True)
            filename = os.path.join(OUTPUT_DIR, f"session_{int(time.time())}.wav")

        self._write_wav(filename, buffer, SAMPLE_RATE)
        self._notes.clear()

    @staticmethod
    def _write_wav(path, samples, sample_rate):
        """Write PCM-16 mono WAV file."""
        n_samples = len(samples)
        data = bytearray()
        for s in samples:
            # Clamp to [-1, 1] and convert to 16-bit PCM
            sample = max(-1.0, min(1.0, s))
            pcm = int(sample * 32767)
            data.extend(struct.pack("<h", pcm))

        n_channels = 1
        bits_per_sample = 16
        byte_rate = sample_rate * n_channels * bits_per_sample // 8
        block_align = n_channels * bits_per_sample // 8
        data_size = n_samples * block_align

        with open(path, "wb") as f:
            # RIFF header
            f.write(b"RIFF")
            f.write(struct.pack("<I", 36 + data_size))
            f.write(b"WAVE")
            # fmt chunk
            f.write(b"fmt ")
            f.write(struct.pack("<I", 16))  # chunk size
            f.write(struct.pack("<H", 1))   # PCM format
            f.write(struct.pack("<H", n_channels))
            f.write(struct.pack("<I", sample_rate))
            f.write(struct.pack("<I", byte_rate))
            f.write(struct.pack("<H", block_align))
            f.write(struct.pack("<H", bits_per_sample))
            # data chunk
            f.write(b"data")
            f.write(struct.pack("<I", data_size))
            f.write(bytes(data))

    @property
    def enabled(self):
        return self._enabled

    @property
    def pending(self):
        return len(self._notes)


audio = Audio()
