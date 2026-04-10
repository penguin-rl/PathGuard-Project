
import cv2
import numpy as np

class MotionEngine:
    def __init__(self):
        self.prev_gray = None
        self.threshold = 3.0  # Balanced Sensitivity
        self.min_area = 2500   # Minimum area
        
        # Persistence
        self.consecutive_frames = 0
        self.required_frames = 3 # Moderate persistence

    def detect(self, frame):
        """
        Detects fast motion in the frame with focus on "Danger Corridor" and Looming.
        Returns: (bool, message)
        """
        # Convert to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
        
        # Resize for faster processing
        small_gray = cv2.resize(gray, (0,0), fx=0.5, fy=0.5)
        height, width = small_gray.shape[:2]

        if self.prev_gray is None:
            self.prev_gray = small_gray
            return False, None

        # Calculate Optical Flow (Farneback)
        flow = cv2.calcOpticalFlowFarneback(self.prev_gray, small_gray, None, 
                                            0.5, 3, 15, 3, 5, 1.2, 0)
        
        # --- GLOBAL MOTION (EGO-MOTION CHECK) ---
        avg_global_x = np.mean(flow[..., 0])
        turning_threshold = 2.0
        is_turning = abs(avg_global_x) > turning_threshold
        
        # --- DANGER CORRIDOR (Unified) ---
        # Focus on the central vertical strip (middle 50% width)
        # and bottom 80% height (entire navigable path)
        mask_corridor = np.zeros_like(small_gray, dtype=np.uint8)
        start_x = int(width * 0.25)
        end_x = int(width * 0.75)
        start_y = int(height * 0.20)
        cv2.rectangle(mask_corridor, (start_x, start_y), (end_x, height), 255, -1)
        
        # Flow Components
        fx = flow[..., 0]
        fy = flow[..., 1]
        
        # Divergence (Looming)
        y_grid, x_grid = np.mgrid[0:height, 0:width]
        center_x, center_y = width // 2, height // 2
        dx = x_grid - center_x
        dy = y_grid - center_y
        divergence = fx * dx + fy * dy
        
        mag, _ = cv2.cartToPolar(fx, fy)
        valid_motion = (mag > self.threshold) & (mask_corridor > 0)
        
        # Analysis
        looming_score = np.sum(divergence[valid_motion] > 0)
        receding_score = np.sum(divergence[valid_motion] < 0)
        lateral_score = np.count_nonzero(valid_motion)
        
        message = None
        detected = False
        current_frame_detected = False
        temp_message = None

        if lateral_score > self.min_area:
             # LOOMING vs RECEDING
             is_looming = looming_score > receding_score * 1.5
             is_receding = receding_score > looming_score * 1.5
             
             if is_looming and looming_score > lateral_score * 0.7:
                 temp_message = "APPROACHING FAST!"
                 current_frame_detected = True
                 
             elif is_receding:
                 # Ignore receding objects
                 pass
                 
             elif not is_turning and lateral_score > self.min_area * 1.2:
                 avg_x = np.mean(fx[valid_motion])
                 if avg_x > 1.0:
                     temp_message = "Motion Right"
                     current_frame_detected = True
                 elif avg_x < -1.0:
                     temp_message = "Motion Left"
                     current_frame_detected = True

        self.prev_gray = small_gray
        
        # Persistence Logic
        if current_frame_detected:
            self.consecutive_frames += 1
        else:
            self.consecutive_frames = 0
            
        if self.consecutive_frames >= self.required_frames:
            return True, temp_message
            
        return False, None
