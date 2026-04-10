
import sys
import time
import threading
import cv2
from camera import Camera, SyntheticCamera
from audio import AudioEngine
from motion import MotionEngine
from path_alignment import PathAlignmentEngine
from risk import RiskArbiter, PRIORITY_INFO, PRIORITY_WARNING, PRIORITY_CRITICAL

import argparse


class OfflineVisionEngine:
    def __init__(self, lang="zh"):
        self.lang = lang

    def analyze_frame(self, frame_rgb):
        return "路徑暢通" if self.lang == "zh" else "Path clear"

def load_vision_engine(lang):
    from vision import VisionEngine
    return VisionEngine(lang=lang)

def main():
    parser = argparse.ArgumentParser(description="PathGuard Demo")
    parser.add_argument("--source", type=str, default="0", help="Camera index, video path, or 'synthetic'")
    parser.add_argument("--lang", type=str, default="zh", choices=["zh", "en"], help="Voice/output language")
    parser.add_argument("--offline", action="store_true", help="Run without Gemini (no API key required)")
    parser.add_argument("--headless", action="store_true", help="Disable window/UI output")
    parser.add_argument("--seconds", type=float, default=0.0, help="Run for N seconds then exit (0 = until quit)")
    parser.add_argument("--motion", dest="enable_motion", action="store_true", help="Enable optical-flow motion alerts")
    parser.add_argument("--no-motion", dest="enable_motion", action="store_false", help="Disable optical-flow motion alerts")
    parser.set_defaults(enable_motion=True)
    args = parser.parse_args()

    # Determine if source is an integer (camera index) or string (file path)
    if args.source == "synthetic":
        source = "synthetic"
    elif args.source.isdigit():
        source = int(args.source)
    else:
        source = args.source

    print(f"Initializing PathGuard using source: {source}...")
    
    # Initialize modules
    try:
        camera = SyntheticCamera() if source == "synthetic" else Camera(source=source)
        audio = AudioEngine()
        vision = OfflineVisionEngine(lang=args.lang) if args.offline else load_vision_engine(args.lang)
        motion = MotionEngine()
        path_alignment = PathAlignmentEngine()
        arbiter = RiskArbiter()
    except Exception as e:
        print(f"Initialization Failed: {e}")
        return

    print("Starting modules...")
    camera.start()
    audio.start()
    audio.speak("啟動完成" if args.lang == "zh" else "Navigation started")

    last_analysis_time = 0
    analysis_interval = 3.0
    
    last_motion_alert = 0
    motion_cooldown = 2.0 # Don't spam motion alerts

    print("Press 'q' to quit." if not args.headless else "Running headless...")

    # Shared variable for the latest result
    state = {"last_result": "Waiting..."}

    enable_motion = bool(args.enable_motion)
    in_flight = {"vision": False}
    start_ts = time.time()
    last_emit = {
        PRIORITY_INFO: {"text": None, "time": 0.0, "cooldown": 3.0},
        PRIORITY_WARNING: {"text": None, "time": 0.0, "cooldown": 1.5},
        PRIORITY_CRITICAL: {"text": None, "time": 0.0, "cooldown": 0.2},
    }
    
    try:
        while True:
            try:
                frame = camera.get_frame()
                current_time = time.time()

                if frame is not None:
                    # Convert back to BGR for OpenCV display
                    display_frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
                    height, width, _ = display_frame.shape

                    motion_event = None
                    if enable_motion:
                        # PASS RAW FRAME BEFORE DRAWING OVERLAYS
                        is_moving, motion_msg = motion.detect(frame)

                        # Visualize Danger Corridor
                        start_x = int(width * 0.25)
                        end_x = int(width * 0.75)
                        cv2.line(display_frame, (start_x, 0), (start_x, height), (0, 255, 255), 1)
                        cv2.line(display_frame, (end_x, 0), (end_x, height), (0, 255, 255), 1)
                        cv2.putText(display_frame, "DANGER CORRIDOR", (start_x + 10, height - 20), 
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)
                        
                        if is_moving and motion_msg:
                            # Flash red border on screen if alert
                            cv2.rectangle(display_frame, (0,0), (width, height), (0,0,255), 10)
                            
                            if (current_time - last_motion_alert > motion_cooldown):
                                print(f"ALERT: {motion_msg}")
                                motion_event = motion_msg
                                last_motion_alert = current_time
                    
                    alignment_msg, alignment_lines = path_alignment.detect(frame)
                    alignment_display = alignment_msg
                    if alignment_msg and args.lang == "zh":
                        if "LEFT" in alignment_msg.upper():
                            alignment_display = "偏右，往左修正"
                        elif "RIGHT" in alignment_msg.upper():
                            alignment_display = "偏左，往右修正"
                        elif "ENDS" in alignment_msg.upper():
                            alignment_display = "路徑結束"
                    if alignment_lines:
                        for p1, p2 in alignment_lines:
                            cv2.line(display_frame, p1, p2, (255, 180, 0), 2)

                    # Add text overlay
                    cv2.rectangle(display_frame, (0, 0), (width, 80), (0, 0, 0), -1)
                    
                    # Sanitize text (remove newlines, extra spaces)
                    display_text = state['last_result'].replace('\n', ' | ').replace('*', '').strip()
                    if len(display_text) > 60:
                        display_text = display_text[:57] + "..."
                        
                    cv2.putText(display_frame, f"Analysis: {display_text}", (10, 40), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2, cv2.LINE_AA)
                    
                    if not enable_motion:
                        cv2.putText(display_frame, "Motion: OFF", (width - 170, 40), 
                              cv2.FONT_HERSHEY_SIMPLEX, 0.7, (100, 100, 100), 2)
                    if alignment_display:
                        cv2.putText(display_frame, alignment_display, (10, 72),
                              cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 200, 255), 2, cv2.LINE_AA)

                    if not args.headless:
                        cv2.imshow("PathGuard (Demo)", display_frame)

                    # Analyze frame periodically
                    if current_time - last_analysis_time > analysis_interval and not in_flight["vision"]:
                        last_analysis_time = current_time
                        in_flight["vision"] = True
                        threading.Thread(
                            target=process_frame_demo,
                            args=(vision, frame, state, in_flight),
                            daemon=True,
                        ).start()

                    event = arbiter.decide(
                        motion=motion_event,
                        alignment=alignment_msg,
                        vision=state.get("last_result") if state.get("last_result") not in (None, "Waiting...") else None,
                        lang=args.lang,
                    )
                    if event is not None:
                        now = time.time()
                        prev = last_emit.get(event.priority)
                        if prev and prev["text"] == event.text and (now - prev["time"]) < prev["cooldown"]:
                            pass
                        else:
                            audio.speak(event.text, interrupt=event.interrupt)
                            arbiter.mark_spoken(event)
                            if prev is not None:
                                prev["text"] = event.text
                                prev["time"] = now

                if not args.headless:
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        break
                if args.seconds and (current_time - start_ts) >= args.seconds:
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
        if not args.headless:
            cv2.destroyAllWindows()
        print("Goodbye.")

def process_frame_demo(vision, frame, state, in_flight):
    """Helper to run vision analysis in background."""
    try:
        result = vision.analyze_frame(frame)
        if result:
            print(f"Detected: {result}")
            state["last_result"] = result
    finally:
        in_flight["vision"] = False

if __name__ == "__main__":
    main()
