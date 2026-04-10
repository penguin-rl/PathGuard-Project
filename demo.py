
import sys
import time
import threading
import cv2
from camera import Camera
from audio import AudioEngine
from vision import VisionEngine
from motion import MotionEngine

import argparse

def main():
    parser = argparse.ArgumentParser(description="Be My Sight Demo")
    parser.add_argument("--source", type=str, default="0", help="Camera index or path to video file")
    args = parser.parse_args()

    # Determine if source is an integer (camera index) or string (file path)
    if args.source.isdigit():
        source = int(args.source)
    else:
        source = args.source

    print(f"Initializing Be My Sight using source: {source}...")
    
    # Initialize modules
    try:
        camera = Camera(source=source)
        audio = AudioEngine()
        vision = VisionEngine()
        motion = MotionEngine()
    except Exception as e:
        print(f"Initialization Failed: {e}")
        return

    print("Starting modules...")
    camera.start()
    audio.start()
    audio.speak("Navigation started. Please wait for camera initialization.")

    last_analysis_time = 0
    analysis_interval = 3.0
    
    last_motion_alert = 0
    motion_cooldown = 2.0 # Don't spam motion alerts

    print("Press 'q' to quit.")

    # Shared variable for the latest result
    state = {"last_result": "Waiting..."}

    # Configuration
    ENABLE_MOTION = False # User requested to disable by default
    
    try:
        while True:
            try:
                frame = camera.get_frame()
                current_time = time.time()

                if frame is not None:
                    # Convert back to BGR for OpenCV display
                    display_frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
                    height, width, _ = display_frame.shape

                    # 1. OPTICAL FLOW (Fast Motion) - Conditional
                    if ENABLE_MOTION:
                        # PASS RAW FRAME BEFORE DRAWING OVERLAYS
                        is_moving, motion_msg = motion.detect(frame)

                        # Visualize Danger Corridor
                        start_x = int(width * 0.25)
                        end_x = int(width * 0.75)
                        cv2.line(display_frame, (start_x, 0), (start_x, height), (0, 255, 255), 1)
                        cv2.line(display_frame, (end_x, 0), (end_x, height), (0, 255, 255), 1)
                        cv2.putText(display_frame, "DANGER CORRIDOR", (start_x + 10, height - 20), 
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)
                        
                        if is_moving:
                            # Flash red border on screen if alert
                            cv2.rectangle(display_frame, (0,0), (width, height), (0,0,255), 10)
                            
                            if (current_time - last_motion_alert > motion_cooldown):
                                print(f"ALERT: {motion_msg}")
                                # Prioritize motion alert AND INTERRUPT existing speech
                                audio.speak(f"Warning: {motion_msg}", interrupt=True)
                                last_motion_alert = current_time
                    
                    # Add text overlay
                    cv2.rectangle(display_frame, (0, 0), (width, 80), (0, 0, 0), -1)
                    
                    # Sanitize text (remove newlines, extra spaces)
                    display_text = state['last_result'].replace('\n', ' | ').replace('*', '').strip()
                    if len(display_text) > 60:
                        display_text = display_text[:57] + "..."
                        
                    cv2.putText(display_frame, f"Analysis: {display_text}", (10, 40), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2, cv2.LINE_AA)
                    
                    if not ENABLE_MOTION:
                         cv2.putText(display_frame, "Motion Detection: OFF", (width - 250, 40), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (100, 100, 100), 2)
                    
                    cv2.imshow("Be My Sight (Demo)", display_frame)

                    # Analyze frame periodically
                    if current_time - last_analysis_time > analysis_interval:
                        last_analysis_time = current_time
                        threading.Thread(target=process_frame_demo, args=(vision, audio, frame, state)).start()

                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
                
                # Small sleep to prevent 100% CPU usage if camera is slow
                time.sleep(0.01)
            
            except Exception as e:
                import traceback
                traceback.print_exc()
                print(f"Error in main loop: {e}")
                time.sleep(1) # Prevent tight loop on error

    except KeyboardInterrupt:
        print("Stopping...")
    finally:
        print("Cleaning up...")
        camera.stop()
        audio.stop()
        cv2.destroyAllWindows()
        print("Goodbye.")

def process_frame_demo(vision, audio, frame, state):
    """Helper to run vision analysis in background."""
    result = vision.analyze_frame(frame)
    if result:
        print(f"Detected: {result}")
        state["last_result"] = result
        audio.speak(result)

if __name__ == "__main__":
    main()
