# PathGuard (路徑守護者) 🛡️

**PathGuard (路徑守護者)** is a real-time AI navigation assistant designed to help everyone, especially blind and visually impaired individuals, navigate the world safely and confidently. 

Using **Google's Gemini 2.0 Flash API** and **OpenCV**, the application analyzes a live camera feed to identify obstacles, sidewalk boundaries, crosswalk signals, and dangerous fast-moving objects. It provides immediate audio feedback to guide the user.

## 📺 Demo Video

[Place your demo video here]

---

## 🔬 Inspiration

This project is inspired by **WalkVLM** (arXiv:2412.20903), which explores using Vision-Language Models (VLMs) to provide walking assistance for visually impaired individuals. Like WalkVLM, **PathGuard** leverages the reasoning capabilities of multimodal AI (Gemini 2.0) to understand complex scenes and provide concise, actionable guidance in real-time.

## ✨ Key Features

*   **Real-time Obstacle Detection**: Identifies cars, people, poles, and other hazards using clock-face positioning (e.g., "Car at 2 o'clock").
*   **Path Alignment**: Guides the user to stay on the sidewalk and warns if they are veering off.
*   **Crosswalk Recognition**: Detects crosswalk signals (Walk/Don't Walk) and traffic lights.
*   **Fast Motion Warnings** (Optional): Uses optical flow to detect fast-approaching objects (cars, bikes) and provides an automated "Warning: APPROACHING FAST" alert.
*   **Audio Interrupts**: Improving safety by allowing critical warnings to interrupt descriptions.

## 🛠️ Prerequisites

*   **Python 3.10+** (Developed on Python 3.13)
*   **Webcam** (Built-in or USB)
*   **Gemini API Key** from [Google AI Studio](https://aistudio.google.com/)
*   **OS**: macOS (Recommended for native audio), Windows, or Linux (requires `pyttsx3`)

## 🚀 Installation

1.  **Clone the repository**:
    ```bash
    git clone <repo_url>
    cd <repo_dir>
    ```

2.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
    *Dependencies include: `google-generativeai`, `opencv-python`, `pillow`, `python-dotenv`.*

3.  **Set up API Key**:
    *   Create a file named `.env` in the project root.
    *   Add your Gemini API key:
        ```env
        GEMINI_API_KEY=your_api_key_here
        ```

## 🎮 Usage

Run the main demo script:

```bash
python demo.py
```

*   **Q**: Quit the application.

### Configuration

You can enable/disable the experimental **Motion Detection** feature (disabled by default for stability) by editing `demo.py`:

```python
# demo.py line 53
ENABLE_MOTION = False  # Set to True to enable fast motion tracking
```

## 🏗️ Architecture

*   `vision.py`: Handles interaction with the Gemini API for scene analysis.
*   `motion.py`: Uses OpenCV Optical Flow for fast motion and looming detection.
*   `audio.py`: Manages text-to-speech output using macOS native `say` command with interruption support.
*   `camera.py`: Thread-safe camera frame capture.
*   `demo.py`: Main application loop integrating all modules.

## 📝 License

[MIT License](LICENSE)
