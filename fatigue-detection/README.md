# 😴 Fatigue Detection System
Real-time drowsiness detection using webcam, MediaPipe face mesh, and Eye Aspect Ratio (EAR).

## Features
- Live webcam feed with eye landmark overlay
- EAR (Eye Aspect Ratio) calculation for blink/closure detection
- Blink rate monitoring (blinks per minute)
- Fatigue score (0–100%) with animated gauge
- Visual + on-screen alert when drowsiness is detected
- Blink history chart (last 20 seconds)
- Event log with timestamped status changes
- Session reset button

## Quick Start

### 1. Install dependencies
```bash
cd fatigue-detection
pip install -r requirements.txt
```

### 2. Run the app
```bash
python app.py
```

### 3. Open in browser
```
http://127.0.0.1:5000
```

## How It Works

### Eye Aspect Ratio (EAR)
```
EAR = (|p2-p6| + |p3-p5|) / (2 × |p1-p4|)
```
- Open eye  → EAR ≈ 0.30–0.45
- Closed eye → EAR < 0.25

### Fatigue Logic
| Condition | Action |
|---|---|
| EAR < 0.25 for 20+ frames | Fatigue score +3/frame |
| Blink rate < 15/min (after 10s) | Fatigue score +1/frame |
| Normal state | Fatigue score −1/frame |
| Score ≥ 70 OR prolonged closure | DROWSY alert |
| Score 40–69 | Tired warning |
| Score < 40 | Awake |

## Project Structure
```
fatigue-detection/
├── app.py            # Flask server + video streaming
├── fatigue_model.py  # EAR logic + FatigueDetector class
├── requirements.txt
├── templates/
│   └── index.html    # Full-featured HUD dashboard
└── README.md
```

## Troubleshooting
- **No camera found**: Make sure no other app is using the webcam. Change `cv2.VideoCapture(0)` to `1` or `2` if you have multiple cameras.
- **Low FPS**: Reduce resolution in `app.py` (`CAP_PROP_FRAME_WIDTH`, `CAP_PROP_FRAME_HEIGHT`).
- **mediapipe install fails**: Try `pip install mediapipe --extra-index-url https://pypi.org/simple`.
