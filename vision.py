
import os
import time
import google.generativeai as genai
from dotenv import load_dotenv
from PIL import Image

# Load environment variables
load_dotenv(override=True)

class VisionEngine:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        genai.configure(api_key=self.api_key)
        
        # Use Gemini 2.0 Flash for speed
        self.model = genai.GenerativeModel('gemini-2.0-flash')
        
        self.prompt = """
        You are a navigation assistant for a blind person.
        Analyze this image from their walking perspective.

        See far ahead for obstacles and signals to warn the user early.

        PRIORITY 1:  & IMMEDIATE OBSTACLES
        - If there is an obstacle coming up: "[Object] ahead at [Clock] o'clock".
        - If there is a person walking towards the user: "Person at [Clock] o'clock".
        - If clear and centered: "Path clear".
        
        PRIORITY 2: CROSSWALK SIGNALS (Red / Green).
        - Scan well ahead for signals: "Crosswalk signal is [State]"

        PRIORITY 3: PATH ALIGNMENT
        - If there's no road ahead: "Path ends".
        - If the user is veering off: "Veering Left", "Veering Right".

        Keep it extremely concise (max 5 words). Do not explain.
        """

    def analyze_frame(self, frame_rgb):
        """
        Analyzes a single frame and returns the text description.
        Args:
            frame_rgb: numpy array of the frame in RGB format.
        """
        try:
            # Resize for speed (Gemini Flash works well with lower res)
            # Convert numpy array to PIL Image
            img = Image.fromarray(frame_rgb)
            img.thumbnail((320, 320)) # Limit max dimension to 640px -> Fast upload
            
            # Generate content
            response = self.model.generate_content([self.prompt, img])
            text = response.text.strip()
            return text
        except Exception as e:
            print(f"Vision Error: {e}")
            return None
