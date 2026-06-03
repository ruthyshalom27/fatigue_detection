import cv2
from flask import Flask, render_template, Response, jsonify, request
from fatigue_model import FatigueDetector
import threading

app = Flask(__name__)

# Global detector instance
detector = FatigueDetector()
frame_lock = threading.Lock()
current_stats = {}

# Video capture
cap = None
video_thread = None
running = False


def init_camera():
    """Initialize camera with proper settings."""
    global cap
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    cap.set(cv2.CAP_PROP_FPS, 30)
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
    return cap.isOpened()


def capture_frames():
    """Continuously capture and process frames from webcam."""
    global current_stats
    
    while running:
        ret, frame = cap.read()
        if not ret:
            continue

        # Process frame through detector
        annotated_frame, stats = detector.process_frame(frame)

        with frame_lock:
            current_stats = stats

        # Encode frame as JPEG
        ret, buffer = cv2.imencode('.jpg', annotated_frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
        frame_data = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n'
               b'Content-Length: ' + str(len(frame_data)).encode() + b'\r\n\r\n' + frame_data + b'\r\n')


@app.route('/')
def index():
    """Render the main dashboard."""
    return render_template('index.html')


@app.route('/video')
def video():
    """Stream MJPEG video feed."""
    return Response(capture_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/stats')
def stats():
    """Return current detection statistics as JSON."""
    with frame_lock:
        return jsonify(current_stats)


@app.route('/reset', methods=['POST'])
def reset():
    """Reset the detector and return success status."""
    detector.reset()
    return jsonify({'status': 'reset', 'message': 'Detector reset successfully'})


def start_video_thread():
    """Start the frame capture thread."""
    global video_thread, running
    running = True
    video_thread = threading.Thread(target=lambda: list(capture_frames()), daemon=True)
    video_thread.start()


if __name__ == '__main__':
    # Initialize camera
    if not init_camera():
        print("ERROR: Could not open webcam. Check camera connection and permissions.")
        exit(1)

    print("✓ Camera initialized successfully")
    print("\n" + "="*60)
    print("  FATIGUE DETECTION SYSTEM - Flask Server")
    print("="*60)
    print("\n  🚀 Starting server...")
    print("  📍 Open browser: http://127.0.0.1:5000")
    print("  ⏹️  To stop: Press Ctrl+C")
    print("\n" + "="*60 + "\n")

    # Note: Video streaming in Flask doesn't need a separate thread
    # The WSGI server will handle the generator
    app.run(debug=False, host='127.0.0.1', port=5000, threaded=True)
