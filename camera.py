import time
import cv2
import threading

class Camera:
    def __init__(self, source=0):
        self.source = source
        self.cap = None
        self.running = False
        self.lock = threading.Lock()
        self.current_frame = None

    def start(self):
        self.cap = cv2.VideoCapture(self.source)
        if not self.cap.isOpened():
            raise RuntimeError(f"Could not open camera or video source: {self.source}")
        
        # Try to get FPS, default to 30 if not available
        self.fps = self.cap.get(cv2.CAP_PROP_FPS)
        if self.fps <= 0 or self.fps > 120:
            self.fps = 15
        self.frame_delay = 1.0 / self.fps

        self.running = True
        self.thread = threading.Thread(target=self._update, daemon=True)
        self.thread.start()

    def _update(self):
        while self.running:
            start_time = time.time()
            ret, frame = self.cap.read()
            if ret:
                with self.lock:
                    self.current_frame = frame
            else:
                # Loop video if it's a file
                if isinstance(self.source, str):
                    self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                    continue

            # Maintain FPS
            elapsed = time.time() - start_time
            if self.frame_delay > elapsed:
                time.sleep(self.frame_delay - elapsed)

    def get_frame(self):
        """Returns the latest frame in RGB format."""
        with self.lock:
            if self.current_frame is not None:
                # Convert BGR to RGB
                return cv2.cvtColor(self.current_frame, cv2.COLOR_BGR2RGB)
            return None

    def stop(self):
        self.running = False
        if self.thread.is_alive():
            self.thread.join()
        if self.cap:
            self.cap.release()


class SyntheticCamera:
    def __init__(self, width=640, height=480, fps=15):
        self.width = int(width)
        self.height = int(height)
        self.fps = float(fps)
        self.frame_delay = 1.0 / self.fps if self.fps > 0 else 0.066
        self.running = False
        self.lock = threading.Lock()
        self.current_frame = None
        self._t = 0

    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self._update, daemon=True)
        self.thread.start()

    def _update(self):
        while self.running:
            start_time = time.time()
            frame = self._render()
            with self.lock:
                self.current_frame = frame
            elapsed = time.time() - start_time
            if self.frame_delay > elapsed:
                time.sleep(self.frame_delay - elapsed)

    def _render(self):
        import numpy as np

        h, w = self.height, self.width
        img = np.zeros((h, w, 3), dtype=np.uint8)
        img[:] = (30, 30, 30)

        left_bottom = (int(w * 0.28), h)
        left_top = (int(w * 0.44), int(h * 0.55))
        right_bottom = (int(w * 0.72), h)
        right_top = (int(w * 0.56), int(h * 0.55))

        cv2.line(img, left_bottom, left_top, (230, 230, 230), 4)
        cv2.line(img, right_bottom, right_top, (230, 230, 230), 4)

        self._t = (self._t + 1) % 240
        drift = int(np.sin(self._t / 30.0) * w * 0.04)
        cv2.line(img, (w // 2 + drift, h), (w // 2 + drift, int(h * 0.55)), (80, 80, 80), 2)

        return cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    def get_frame(self):
        with self.lock:
            return None if self.current_frame is None else self.current_frame.copy()

    def stop(self):
        self.running = False
        if hasattr(self, "thread") and self.thread.is_alive():
            self.thread.join()
