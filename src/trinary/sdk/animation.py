from trinary.sdk.constants import FPS


class Animation:
    def __init__(self, frames, frame_duration=None, loop=True):
        self.frames = list(frames)
        self.frame_duration = frame_duration if frame_duration is not None else FPS // 2
        self.loop = loop
        self._current_frame = 0
        self._timer = 0
        self._playing = False
        self._finished = False

    def play(self):
        self._playing = True
        self._current_frame = 0
        self._timer = 0
        self._finished = False

    def stop(self):
        self._playing = False

    def pause(self):
        self._playing = False

    def resume(self):
        self._playing = True

    def update(self):
        if not self._playing or self._finished:
            return
        self._timer += 1
        if self._timer >= self.frame_duration:
            self._timer = 0
            self._current_frame += 1
            if self._current_frame >= len(self.frames):
                if self.loop:
                    self._current_frame = 0
                else:
                    self._current_frame = len(self.frames) - 1
                    self._finished = True
                    self._playing = False

    def current_frame(self):
        if self._finished and not self.loop:
            return self.frames[-1]
        return self.frames[self._current_frame]

    def reset(self):
        self._current_frame = 0
        self._timer = 0
        self._finished = False

    def is_finished(self):
        return self._finished
