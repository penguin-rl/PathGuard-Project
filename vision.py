
import os
import time
try:
    from google import genai as genai
    _GENAI_MODE = "new"
except Exception:
    import google.generativeai as genai
    _GENAI_MODE = "legacy"
from dotenv import load_dotenv
from PIL import Image

# Load environment variables
load_dotenv(override=True)

class VisionEngine:
    def __init__(self, lang="zh"):
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        if _GENAI_MODE == "legacy":
            genai.configure(api_key=self.api_key)
        else:
            self.client = genai.Client(api_key=self.api_key)
        
        # Use Gemini 2.0 Flash for speed
        self.model_name = "gemini-2.0-flash"
        if _GENAI_MODE == "legacy":
            self.model = genai.GenerativeModel(self.model_name)
        
        self.lang = lang
        self.prompt = self._build_prompt(lang)

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
            if _GENAI_MODE == "legacy":
                response = self.model.generate_content([self.prompt, img])
                text = getattr(response, "text", "") or ""
            else:
                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=[self.prompt, img],
                )
                text = getattr(response, "text", "") or ""

            return self._postprocess(text)
        except Exception as e:
            print(f"Vision Error: {e}")
            return None

    def _build_prompt(self, lang):
        if lang == "en":
            return """
You are a real-time navigation assistant for safe walking.
Analyze the image from the user's walking perspective.

Output rules:
- Max 5 words per segment.
- Use clock-direction (1-12 o'clock).
- If multiple items, join segments with " | ".
- No explanations.

Priority:
1) Immediate obstacles:
   - "[Object] at [Clock] o'clock"
   - "Person at [Clock] o'clock"
   - "Path clear"
2) Crosswalk signals:
   - "Crosswalk is [red/green]"
3) Path status:
   - "Path ends"
"""
        return """
你是一個即時行走安全助理。
請用使用者行走視角分析影像。

輸出規則：
- 每段最多 5 個字詞
- 使用時鐘方位（1～12 點鐘方向）
- 多段資訊用「 | 」分隔
- 不要解釋

優先順序：
1）立即障礙：
   - 「[物件] 在 [X] 點鐘方向」
   - 「行人 在 [X] 點鐘方向」
   - 「路徑暢通」
2）斑馬線號誌：
   - 「斑馬線 [紅/綠]」
3）路徑狀態：
   - 「路徑結束」
"""

    def _postprocess(self, text):
        out = (text or "").replace("\n", " ").replace("*", " ").strip()
        while "  " in out:
            out = out.replace("  ", " ")
        if len(out) > 120:
            out = out[:120].rstrip()
        return out or None
