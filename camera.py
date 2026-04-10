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
