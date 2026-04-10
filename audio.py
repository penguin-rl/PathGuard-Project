import subprocess
import threading
import queue
import time
import platform

# Only import pyttsx3 if not on Mac or if prefered
try:
    import pyttsx3
    HAS_PYTTSX3 = True
except ImportError:
    HAS_PYTTSX3 = False

class AudioEngine:
    def __init__(self):
        self.queue = queue.Queue(maxsize=3) # Limit queue to 3 items
        self.running = False
        self.thread = None
        self.current_process = None
        self.lock = threading.Lock()
        self.system = platform.system()
        
        # Fallback engine for non-macOS
        self.engine = None
        if self.system != "Darwin" and HAS_PYTTSX3:
            self.engine = pyttsx3.init()

    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()

    def stop(self):
        self.running = False
        if self.current_process:
            try:
                self.current_process.terminate()
            except:
                pass
        if self.thread:
            self.thread.join()

    def speak(self, text, interrupt=False):
        """
        Adds text to the speech queue.
        If interrupt=True, stops current speech and clears queue.
        """
        if interrupt:
            with self.lock:
                # 1. Clear the queue
                while not self.queue.empty():
                    try:
                        self.queue.get_nowait()
                        self.queue.task_done()
                    except queue.Empty:
                        break
                
                # 2. Stop current speech
                if self.system == "Darwin":
                     if self.current_process and self.current_process.poll() is None:
                        try:
                            self.current_process.terminate()
                        except:
                            pass
                elif self.engine:
                    # pyttsx3 stop is tricky/blocking sometimes, but try it
                    try:
                        self.engine.stop()
                    except:
                        pass
            
            self.queue.put(text)
        else:
            # Normal speech: Prioritize LATEST info.
            # If queue is full, drop the OLDEST item to make room for the NEWEST.
            if self.queue.full():
                try:
                    self.queue.get_nowait()
                    self.queue.task_done()
                except queue.Empty:
                    pass
            self.queue.put(text)

    def _run(self):
        while self.running:
            try:
                text = self.queue.get(timeout=0.1)
                
                if self.system == "Darwin":
                    # macOS Native (Subprocess - Stable)
                    # Fix: Sanitize text to prevent "invalid option" errors if text starts with "-"
                    safe_text = text.strip()
                    if safe_text.startswith("-"):
                        safe_text = " " + safe_text 
                        
                    with self.lock:
                        self.current_process = subprocess.Popen(["say", safe_text])
                    
                    try:
                        # Add Timeout to prevent hanging forever
                        self.current_process.wait(timeout=5) 
                    except subprocess.TimeoutExpired:
                        print("Audio timed out, killing...")
                        if self.current_process:
                            self.current_process.kill()
                    except:
                        pass
                        
                elif self.engine:
                    # Windows/Linux (pyttsx3)
                    # Note: pyttsx3 runAndWait blocks, but that's expected here in the thread
                    try:
                        self.engine.say(text)
                        self.engine.runAndWait()
                    except Exception as e:
                        print(f"pyttsx3 Error: {e}")
                else:
                    print(f"Audio Output (Mock): {text}")
                
                self.queue.task_done()
                time.sleep(0.1)
                
            except queue.Empty:
                continue
            except Exception as e:
                print(f"Audio Error: {e}")
