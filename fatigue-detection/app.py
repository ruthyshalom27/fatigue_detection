from flask import Flask, render_template, Response, jsonify
import cv2
import json
from fatigue_model import FatigueDetector

app = Flask(__name__)

camera   = None
detector = FatigueDetector()
latest_stats = {}

def get_camera():
    global camera
    if camera is None or not camera.isOpened():
        camera = cv2.VideoCapture(0)
        camera.set(cv2.CAP_PROP_FRAME_WIDTH,  640)
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

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video')
def video():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/stats')
def stats():
    return jsonify(latest_stats)

@app.route('/reset', methods=['POST'])
def reset():
    detector.reset()
    return jsonify({"status": "reset ok"})

if __name__ == '__main__':
    print("=" * 50)
    print("  Fatigue Detection System")
    print("  Open: http://127.0.0.1:5000")
    print("=" * 50)
    app.run(debug=True, threaded=True)
