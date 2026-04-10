
import sys
import time
import threading
import cv2
from camera import Camera
from audio import AudioEngine
from vision import VisionEngine

def main():
    print("Initializing Be My Sight...")
    
    # Initialize modules
    try:
        camera = Camera()
        audio = AudioEngine()
        vision = VisionEngine()
    except Exception as e:
        print(f"Initialization Failed: {e}")
        return

    print("Starting modules...")
    camera.start()
    audio.start()
    audio.speak("Navigation started. Please wait for camera initialization.")

    last_analysis_time = 0
    analysis_interval = 3.0  # Analyze every 2 seconds to manage API quota and latency

    print("Press 'q' to quit.")

    try:
        while True:
            frame = camera.get_frame()
            current_time = time.time()

            if frame is not None:
                # show the frame for debugging purposes
                # Convert back to BGR for OpenCV display
                # display_frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
                # cv2.imshow("Be My Sight (Debug)", display_frame)

                # Analyze frame periodically
                if current_time - last_analysis_time > analysis_interval:
                    last_analysis_time = current_time
                    
                    # Run analysis in a separate thread to not block the UI/Camera loop
                    # However, for simplicity in this V1, strictly speaking we might block this loop if not careful.
                    # Ideally, we submit to a thread pool. Let's do a simple threading approach.
                    threading.Thread(target=process_frame, args=(vision, audio, frame)).start()

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            
            # Small sleep to prevent 100% CPU usage if camera is slow
            time.sleep(0.01)

    except KeyboardInterrupt:
        print("Stopping...")
    finally:
        print("Cleaning up...")
        camera.stop()
        audio.stop()
        cv2.destroyAllWindows()
        print("Goodbye.")

def process_frame(vision, audio, frame):
    """Helper to run vision analysis in background."""
    result = vision.analyze_frame(frame)
    if result:
        print(f"Detected: {result}")
        audio.speak(result)

if __name__ == "__main__":
    main()
