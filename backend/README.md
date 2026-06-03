# Fatigue Detection System - Backend API

Flask-based REST API for real-time fatigue detection via computer vision.

## Features
- Real-time video stream processing with OpenCV
- Eye Aspect Ratio (EAR) calculation for fatigue detection
- Blink rate monitoring
- Face detection with Haar Cascades
- MJPEG video streaming endpoint
- JSON stats API
- CORS enabled for web and mobile clients

## Prerequisites
- Python 3.8+
- Webcam/USB camera connected

## Installation

### 1. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

## Running the Backend

### Development
```bash
python app.py
```

Server will start at `http://localhost:5000`

### Production (Gunicorn)
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## API Endpoints

### Video Stream
```
GET /api/video
```
Returns MJPEG stream of video frames with fatigue detection overlays.

**Response**: `multipart/x-mixed-replace` stream

**Example**:
```html
<img src="http://localhost:5000/api/video" />
```

### Statistics
```
GET /api/stats
```
Returns current fatigue detection metrics.

**Response** (JSON):
```json
{
  "status": "Awake",           # Status: "Awake", "Tired", or "DROWSY"
  "fatigue_score": 25,         # 0-100 (higher = more fatigued)
  "ear": 0.35,                 # Eye Aspect Ratio
  "blink_rate": 18.5,          # Blinks per minute
  "blink_count": 12,           # Total blinks detected
  "face_detected": true,       # Whether a face is currently detected
  "closed_frames": 0,          # Frames with closed eyes
  "timestamp": 1686753421.2345 # Unix timestamp
}
```

### Health Check
```
GET /api/health
```
Returns API health status.

**Response** (JSON):
```json
{
  "status": "ok"
}
```

### Status
```
GET /api/status
```
Returns API and system status.

**Response** (JSON):
```json
{
  "status": "running",
  "camera_available": true,
  "current_stats": { /* stats object */ }
}
```

## Configuration

Edit `app.py` to configure:
- Camera resolution: `camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)`
- FPS: `camera.set(cv2.CAP_PROP_FPS, 30)`
- JPEG quality: `cv2.IMWRITE_JPEG_QUALITY, 85`

Edit `fatigue_model.py` for detection thresholds:
- `EAR_THRESHOLD = 0.25` - Eye closure threshold
- `CLOSED_FRAME_THRESHOLD = 20` - Frames for prolonged closure alert

## Detection Algorithm

1. **Face Detection**: Uses OpenCV Haar Cascade (`haarcascade_frontalface_default.xml`)
2. **Eye Detection**: Uses OpenCV Haar Cascade (`haarcascade_eye.xml`)
3. **Eye Aspect Ratio**: Calculates from eye contours to detect closure
4. **Blink Rate**: Tracks blinks per minute over 30-second window
5. **Fatigue Scoring**: Combines EAR, blink rate, and face detection into 0-100 score

## CORS Configuration

Currently enabled for all origins. For production, restrict in `app.py`:

```python
CORS(app, resources={
    r"/api/*": {
        "origins": ["https://yourdomain.com"],
        "methods": ["GET"]
    }
})
```

## Troubleshooting

### Camera not detected
- Check if camera is connected: `lsusb` (Linux) or Device Manager (Windows)
- Ensure no other app is using the camera

### Low FPS / Lag
- Reduce frame resolution in `app.py`
- Lower JPEG quality: change `IMWRITE_JPEG_QUALITY` to 70
- Reduce polling interval in client apps

### No face detected
- Ensure good lighting
- Keep face centered in camera
- Adjust cascade parameters if needed

## Performance Notes

- Single-threaded processing: ~30 FPS at 640x480
- Memory usage: ~200MB at baseline
- Network bandwidth: ~1-2 Mbps for video stream

## Production Deployment

### Docker
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "app.py"]
```

Build: `docker build -t fatigue-api .`
Run: `docker run -d -p 5000:5000 --device /dev/video0 fatigue-api`

## License
MIT
