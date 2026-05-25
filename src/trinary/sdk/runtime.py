import time


class Runtime:
    def __init__(self, engine, target_fps=60):
        self.engine = engine
        self.target_fps = target_fps
        self.frame_time = 1.0 / target_fps
        self._running = False
        self._paused = False
        self._frame_count = 0
        self._fps_timer = 0
        self._display_fps = 0
        self._accumulator = 0.0
        self._last_time = 0.0

    def run(self, update_fn=None, render_fn=None):
        self._running = True
        self._last_time = time.time()
        self._accumulator = 0.0
        self.engine.init()
        while self._running:
            current = time.time()
            frame_delta = current - self._last_time
            self._last_time = current
            if not self._paused:
                self._accumulator += frame_delta
                while self._accumulator >= self.frame_time:
                    if update_fn:
                        update_fn()
                    self.engine.update()
                    self._accumulator -= self.frame_time
                if render_fn:
                    render_fn()
                self.engine.render()
                self._frame_count += 1
            else:
                time.sleep(0.01)

    def run_frame(self, update_fn=None, render_fn=None):
        if not self._running:
            return
        current = time.time()
        if self._last_time == 0:
            self._last_time = current
        frame_delta = current - self._last_time
        self._last_time = current
        if not self._paused:
            self._accumulator += frame_delta
            while self._accumulator >= self.frame_time:
                if update_fn:
                    update_fn()
                self.engine.update()
                self._accumulator -= self.frame_time
            if render_fn:
                render_fn()
            self.engine.render()
            self._frame_count += 1

    def stop(self):
        self._running = False

    def pause(self):
        self._paused = True

    def resume(self):
        self._paused = False

    @property
    def fps(self):
        return int(1.0 / self.frame_time) if self.frame_time > 0 else 0

    def get_frame_count(self):
        return self._frame_count
