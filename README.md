# Fatigue Detection System

A real-time web application that detects driver/student drowsiness using computer vision. The system tracks eye blink rate and Eye Aspect Ratio (EAR) using MediaPipe face mesh landmarks to provide live alerting.

A comprehensive **Mobile & Web App Project** for real-time driver/worker fatigue detection using computer vision and machine learning.

```
📱 Mobile App (React Native)  →  🌐 Web App (HTML/JS)  →  🐍 Backend API (Flask)
                                                                     ↓
                                                            📹 Camera & Detection
```

## Project Structure

```
fatigue-detection/
├── backend/                    # REST API Server (Python/Flask)
│   ├── app.py                 # Flask app with API endpoints
│   ├── fatigue_model.py       # Face detection & EAR calculation
│   ├── requirements.txt
│   └── README.md
│
├── web/                        # Web Application (HTML/CSS/JS)
│   ├── templates/
│   │   └── index.html         # Main web interface
│   ├── static/
│   │   ├── styles.css         # Styling & animations
│   │   └── app.js             # Client-side logic
│   └── README.md
│
└── mobile/                     # Mobile App (React Native)
    └── fatigue-detection-app/
        ├── App.js             # App entry point
        ├── package.json
        ├── src/
        │   ├── config.js      # API configuration
        │   └── screens/       # UI screens
        └── README.md
```

## Features

### Backend
- ✅ Real-time video processing (30 FPS)
- ✅ Eye Aspect Ratio (EAR) detection
- ✅ Blink rate calculation
- ✅ Face detection with Haar Cascades
- ✅ MJPEG video streaming
- ✅ JSON REST API
- ✅ CORS enabled for web/mobile

### Web App
- ✅ Live video stream display
- ✅ Real-time metrics dashboard
- ✅ Animated fatigue gauge
- ✅ Eye metric visualization
- ✅ Event logging
- ✅ Connection status indicator
- ✅ Responsive design

### Mobile App
- ✅ Live monitoring screen
- ✅ Detailed statistics view
- ✅ Real-time metrics
- ✅ Cross-platform (iOS/Android)
- ✅ Offline-ready architecture

## Project Structure

```
fatigue-detection/
├── app.py                 # Flask web server and MJPEG streaming
├── fatigue_model.py       # Core fatigue detection logic
├── requirements.txt       # Python dependencies
├── templates/
│   └── index.html        # Dashboard UI (HUD-style)
└── README.md             # This file
```

## Technical Details

### Eye Aspect Ratio (EAR)

The Eye Aspect Ratio is calculated using six eye landmark points from each eye:

```
EAR = (|p2-p6| + |p3-p5|) / (2 * |p1-p4|)
```

Where:
- `p1-p6` are the six eye landmarks detected by MediaPipe Face Mesh
- Vertical distances between eyelids are measured
- Horizontal distance between eye corners is measured

**Interpretation:**
- EAR > 0.25: Eyes are open
- EAR ≤ 0.25: Eyes are closed

### Fatigue Score Calculation

| Condition | Score Change | Notes |
|-----------|--------------|-------|
| Prolonged closure (20+ frames) | +3 | Most significant fatigue indicator |
| Low blink rate (<15/min) | +1 | Checked after 10 seconds |
| Normal state | -1 | Gradual recovery when alert |
| No face detected | +2 | Cannot monitor without face |

**Score Range:** 0-100
- Score increases with fatigue indicators
- Score decreases naturally during normal, alert operation
- Status updates automatically at thresholds: 40 (Tired), 70 (Drowsy)

### MediaPipe Configuration

Using **legacy API** (`mp.solutions.face_mesh`):
- Max faces: 1
- Refined landmarks: Enabled for better precision
- Detection confidence: 0.5
- Tracking confidence: 0.5

**Eye Landmark Indices:**
- **Left eye:** [33, 160, 158, 133, 153, 144]
- **Right eye:** [362, 385, 387, 263, 373, 380]

## Installation

### Requirements
- Python 3.8 or higher (tested with 3.12)
- Webcam
- 2GB+ RAM

### Step 1: Clone or Extract
```bash
cd fatigue-detection
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

**Required packages:**
- `opencv-python>=4.8.0` - Video capture and frame processing
- `mediapipe==0.10.9` - Face mesh and facial landmarks
- `flask>=3.0.0` - Web framework
- `numpy>=1.24.0` - Numerical operations

### Step 3: Verify Webcam
Ensure your webcam is connected and accessible. Test with:
```bash
python -c "import cv2; cap = cv2.VideoCapture(0); print('✓ Camera OK' if cap.isOpened() else '✗ Camera Failed')"
```

## Running the Application

### Start the Server
```bash
python app.py
```

Expected output:
```
✓ Camera initialized successfully

============================================================
  FATIGUE DETECTION SYSTEM - Flask Server
============================================================

  🚀 Starting server...
  📍 Open browser: http://127.0.0.1:5000
  ⏹️  To stop: Press Ctrl+C

============================================================
```

### Access the Dashboard
1. Open your web browser
2. Navigate to: **http://127.0.0.1:5000**
3. Grant camera permissions when prompted
4. Monitor real-time detection

### Stop the Server
Press `Ctrl+C` in the terminal.

## API Endpoints

### GET `/`
Returns the dashboard HTML page.

### GET `/video`
Streams MJPEG video feed from the webcam with overlaid detection data.
- Content-Type: `multipart/x-mixed-replace`
- JPEG quality: 85
- Resolution: 640x480
- Frame rate: ~30 FPS

### GET `/stats`
Returns current detection statistics as JSON.

**Response Example:**
```json
{
  "face_detected": true,
  "status": "Awake",
  "fatigue_score": 25,
  "ear": 0.42,
  "blink_rate": 18.5,
  "blink_count": 42,
  "closed_frames": 2,
  "timestamp": 1714570123.456
}
```

### POST `/reset`
Resets the detector to initial state and clears all statistics.

**Response:**
```json
{
  "status": "reset",
  "message": "Detector reset successfully"
}
```

## Dashboard Features

### Visual Indicators
- **Live Dot**: Green pulsing dot indicates system is active
- **Corner Brackets**: Cyan decorative brackets frame the video
- **Alert Border**: Red flashing border when DROWSY status detected
- **Scan Lines**: Subtle animated scan lines overlay (HUD effect)

### Gauge
- **Animated SVG** showing fatigue score 0-100%
- Color-coded: Green (Awake) → Yellow (Tired) → Red (Drowsy)

### Eye Metrics
- **Face Detected**: Shows if face is tracked
- **Closed Frames**: Current consecutive eye closure count
- **EAR Progress Bar**: Visual representation of current EAR vs threshold

### Blink History Chart
- 20-second rolling window (20 buckets, 1-second intervals)
- Bar height represents blinks per minute
- Updates every 500ms

### Event Log
- Timestamped status changes
- Scrollable history (max 10 entries)
- Useful for pattern analysis

### Bottom Status Bar
- **Status**: Current alert level (Awake/Tired/DROWSY)
- **EAR Value**: Current Eye Aspect Ratio
- **Blinks/min**: Current blink rate
- **Total Blinks**: Cumulative blink count since start/reset

## Troubleshooting

### Camera Not Found
**Error:** "ERROR: Could not open webcam"

**Solutions:**
1. Check if webcam is physically connected
2. Verify no other application is using the camera
3. Try a different camera index (edit `app.py`, change `cv2.VideoCapture(0)` to `cv2.VideoCapture(1)`)
4. On Linux, ensure user has `/dev/video*` permissions
5. On macOS, grant camera permission in System Preferences

### MediaPipe Import Error
**Error:** "ModuleNotFoundError: No module named 'mediapipe'"

**Solutions:**
```bash
# Reinstall mediapipe
pip uninstall mediapipe -y
pip install mediapipe==0.10.9
```

### Poor Face Detection
**Issue:** Face not detected or landmarks are inaccurate

**Solutions:**
1. Ensure adequate lighting (natural daylight preferred)
2. Face should be directly facing camera within 60cm
3. Clean camera lens
4. Verify MediaPipe confidence thresholds in `fatigue_model.py`
5. Try adjusting `min_detection_confidence` (0.3-0.7 range)

### High CPU Usage
**Issue:** System consuming excessive CPU

**Solutions:**
1. Reduce resolution: Edit `app.py` and lower `FRAME_WIDTH`/`FRAME_HEIGHT`
2. Reduce FPS: Lower `FPS` setting in `app.py`
3. Reduce JPEG quality: Change `[cv2.IMWRITE_JPEG_QUALITY, 85]` to higher value (90-95)
4. Disable browser hardware acceleration if needed

### Browser Won't Connect
**Error:** "Cannot connect to http://127.0.0.1:5000"

**Solutions:**
1. Verify Flask server is running (check terminal for startup message)
2. Use `http://localhost:5000` instead of IP address
3. Check firewall isn't blocking port 5000
4. If using VM, ensure network settings allow local access

### No Video Feed in Dashboard
**Issue:** Video stream area is blank or shows errors

**Solutions:**
1. Check browser console for errors (F12)
2. Verify `/video` endpoint is accessible: Open `http://127.0.0.1:5000/video` directly
3. Check camera permissions in browser
4. Try different browser (Chrome/Firefox recommended)

## Performance Notes

- **Resolution:** 640x480 provides good accuracy vs performance balance
- **FPS:** 30 FPS is optimal for real-time detection
- **Update Rate:** Dashboard polls statistics every 500ms
- **Memory:** Typically <200MB RAM usage
- **GPU:** Not required; CPU detection runs at 15-25 FPS on modern processors

## Limitations & Future Improvements

### Current Limitations
- Single face detection only (max_num_faces=1)
- Requires direct face-forward camera view
- Sensitive to lighting conditions
- No multi-user support

### Potential Enhancements
- Multi-face support for group monitoring
- Head pose estimation for profile views
- Yawning detection
- Recording/export of statistics
- Alert sound notifications
- Historical data dashboard
- Mobile app integration
- ML-based driver profile adaptation

## License

This project is provided as-is for educational and development purposes.

## References

- **MediaPipe:** https://mediapipe.dev
- **OpenCV:** https://opencv.org
- **Flask:** https://flask.palletsprojects.com
- **Eye Aspect Ratio Paper:** "Real-Time Eye Blink Detection using Facial Landmarks" (Tereza Soukupová, Jan Čech)

## Support

For issues, ensure:
1. All dependencies are installed correctly
2. Python version is 3.8+
3. Webcam is functioning properly
4. Adequate lighting is available
5. MediaPipe is version 0.10.9 (legacy API)

---

**Last Updated:** May 2026
**Status:** Production Ready ✓
