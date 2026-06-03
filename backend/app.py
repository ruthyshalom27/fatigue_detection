from flask import Flask, Response, jsonify
from flask_cors import CORS
import cv2
import json
from fatigue_model import FatigueDetector
import threading

app = Flask(__name__)

# Enable CORS for all routes (needed for mobile and web clients)
CORS(app, resources={
    r"/api/*": {
        "origins": "*",
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})

camera = None
detector = FatigueDetector()
latest_stats = {}
camera_lock = threading.Lock()

def get_camera():
    global camera
    with camera_lock:
        if camera is None or not camera.isOpened():
            camera = cv2.VideoCapture(0)
            camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            camera.set(cv2.CAP_PROP_FPS, 30)
    return camera

def generate_frames():
    global latest_stats
    cam = get_camera()
    while True:
        success, frame = cam.read()
        if not success:
            break

        frame, stats = detector.process_frame(frame)
        latest_stats = stats

        ret, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
        if not ret:
            continue

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')

# ── API ENDPOINTS ──

@app.route('/api/video', methods=['GET'])
def video():
    """Stream video frames from camera"""
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/api/stats', methods=['GET'])
def stats():
    """Get current fatigue detection statistics"""
    return jsonify(latest_stats)

@app.route('/api/status', methods=['GET'])
def status():
    """Get API health status"""
    return jsonify({
        'status': 'running',
        'camera_available': camera is not None and camera.isOpened(),
        'current_stats': latest_stats
    })

@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint for load balancers"""
    return jsonify({'status': 'ok'}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
