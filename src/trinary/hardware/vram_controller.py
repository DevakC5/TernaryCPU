"""VRAM controller — bandwidth limits, scanline timing, display sync."""


class VRAMController:
    """Controls VRAM access with bandwidth limits and display timing.

    Simulates:
    - VRAM bandwidth limit (bytes/frame)
    - Scanline traversal timing
    - 30 FPS frame timing
    - Write queue / stalling when CPU writes too fast
    """

    def __init__(self, width_px=64, height_px=64, fps=30, bandwidth_bytes_per_frame=4096):
        self.width_px = width_px
        self.height_px = height_px
        self.fps = fps
        self.bandwidth_bytes_per_frame = bandwidth_bytes_per_frame
        self._write_bytes_this_frame = 0
        self._scanline = 0
        self._frame = 0
        self._cycle = 0
        self._stalled_cycles = 0
        self.total_writes = 0
        self.total_reads = 0
        self._frame_ticks = 0

    @property
    def cycles_per_frame(self):
        return 1000000 // self.fps

    @property
    def scanlines_per_frame(self):
        return self.height_px

    @property
    def cycles_per_scanline(self):
        return self.cycles_per_frame // max(1, self.scanlines_per_frame)

    def tick(self):
        """Advance one cycle of VRAM timing.

        Returns:
            dict with current scanline/frame info.
        """
        self._cycle += 1
        self._frame_ticks += 1
        if self._frame_ticks >= self.cycles_per_frame:
            self._frame += 1
            self._frame_ticks = 0
            self._write_bytes_this_frame = 0
            self._scanline = 0
        self._scanline = (self._frame_ticks // self.cycles_per_scanline) % self.scanlines_per_frame
        return {
            "frame": self._frame,
            "scanline": self._scanline,
            "frame_ticks": self._frame_ticks,
            "write_bytes": self._write_bytes_this_frame,
        }

    def check_write(self, num_bytes=1):
        """Check if a write of num_bytes is allowed this frame.

        Returns:
            bool: True if write allowed, False if bandwidth exceeded (stall).
        """
        if self._write_bytes_this_frame + num_bytes > self.bandwidth_bytes_per_frame:
            self._stalled_cycles += 1
            return False
        self._write_bytes_this_frame += num_bytes
        self.total_writes += num_bytes
        return True

    def read_ok(self):
        self.total_reads += 1
        return True

    @property
    def bandwidth_used_pct(self):
        return (self._write_bytes_this_frame / max(1, self.bandwidth_bytes_per_frame)) * 100

    @property
    def stalled(self):
        return self._stalled_cycles > 0

    def reset(self):
        self._write_bytes_this_frame = 0
        self._scanline = 0
        self._frame = 0
        self._cycle = 0
        self._stalled_cycles = 0
        self.total_writes = 0
        self.total_reads = 0

    def stats(self):
        return {
            "fps": self.fps,
            "resolution": f"{self.width_px}x{self.height_px}",
            "frame": self._frame,
            "scanline": self._scanline,
            "bandwidth_per_frame": self.bandwidth_bytes_per_frame,
            "bandwidth_used_pct": self.bandwidth_used_pct,
            "total_writes": self.total_writes,
            "total_reads": self.total_reads,
            "stalled_cycles": self._stalled_cycles,
        }
