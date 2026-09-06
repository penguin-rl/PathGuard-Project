# Project Name
PathGuard

# Project Overview
PathGuard is a real-time AI path-safety assistant. Through real-time visual understanding and dynamic obstacle detection, it outputs interruptible, actionable short-sentence voice guidance to help users navigate street environments more safely.

# Feature List
- **Real-time video capture**: supports `--source 0` (camera), `--source <video_path>` (video file), or `--source synthetic` (synthetic test source)
- **Scene semantic understanding (Gemini 2.0 Flash)**: outputs concise instructions using clock-position bearings, with a default analysis interval of 3 seconds
- **Dynamic hazard detection (OpenCV Optical Flow)**: focuses on the central walkway region, detects rapid approach and significant displacement; hazard events can interrupt and override ongoing voice playback
- **Path alignment (OpenCV boundary estimation)**: estimates offset from the center of the safe corridor, outputs "Veering Left / Veering Right" correction prompts
- **Risk arbitration**: priority order is "Hazard > Veering > General description"
- **Cross-platform voice output**: uses `say` on macOS, `pyttsx3` on Windows/Linux

# Technical Architecture
`Camera` (real-time video) → `MotionEngine` (optical flow dynamics) and `PathAlignmentEngine` (corridor offset) → `VisionEngine` (Gemini scene understanding) → `RiskArbiter` (risk prioritization) → `AudioEngine` (TTS and interruptible playback)

# Project Structure
- `demo.py`: Main program (integrates video, motion detection, path alignment, Gemini, voice, risk arbitration)
- `camera.py`: Camera source and `SyntheticCamera`
- `vision.py`: Gemini image analysis
- `motion.py`: OpenCV optical flow motion detection
- `path_alignment.py`: OpenCV path alignment
- `risk.py`: Risk arbitration and priority events
- `audio.py`: TTS and `interrupt=True` interruption mechanism
- `requirements.txt`: Python dependencies
- `.env.example`: Environment variable example

# Local Testing Guide
The following workflow has been verified to run on macOS (Python 3.13).

1. Install dependencies
```bash
python3 -m pip install -r requirements.txt
```
2. Offline quick self-test (no camera required, no `GEMINI_API_KEY` required)
```bash
python3 demo.py --source synthetic --offline --headless --seconds 2
```
3. Enable optical flow detection (offline, synthetic source)
```bash
python3 demo.py --source synthetic --offline --headless --seconds 2 --motion
```

## Parameter Description
- `--source`: video source, supports `0` (default camera), a video file path, or `synthetic` (synthetic source)
- `--offline`: do not call Gemini (no `GEMINI_API_KEY` required)
- `--lang`: language, supports `zh` or `en`
- `--motion` / `--no-motion`: enable/disable optical flow motion alerts
- `--headless`: do not open a window (suitable for quick smoke tests)
- `--seconds`: automatically exit after N seconds (`0` means run until manually exited)

# Environment Variables
- `GEMINI_API_KEY`: Gemini API key (required only when cloud-based scene understanding is enabled)

See `.env.example` for reference; create your own `.env` and set `GEMINI_API_KEY`.

# Coolify Deployment Guide
This project does not currently provide a verified Coolify deployment workflow.

# Frontend / Backend Detailed Documentation Links
- Frontend: None (currently a single Python prototype)
- Backend: None (currently a single Python prototype)
