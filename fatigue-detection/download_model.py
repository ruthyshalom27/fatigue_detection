import urllib.request
import os
import sys

# Create models directory
models_dir = os.path.expanduser("~/.mediapipe/models")
os.makedirs(models_dir, exist_ok=True)

# Try different possible URLs for the face landmarker model
urls = [
    "https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker.task",
    "https://storage.googleapis.com/mediapipe-models/face_landmarker_v2_with_blendshapes/float16.tflite",
    "https://download.mediapipe.dev/models/face_landmarker/face_landmarker.task"
]

model_path = os.path.join(models_dir, "face_landmarker.task")

print(f"Models directory: {models_dir}")
print(f"Attempting to download face landmarker model...\n")

success = False
for url in urls:
    try:
        print(f"Trying: {url}")
        urllib.request.urlretrieve(url, model_path)
        print(f"✓ Model downloaded successfully")
        print(f"Model path: {model_path}")
        print(f"File size: {os.path.getsize(model_path)} bytes")
        success = True
        break
    except Exception as e:
        print(f"✗ Failed: {type(e).__name__}")

if not success:
    print("\n✗ Could not download model from any URL")
    print("Trying alternative: checking if model exists in site-packages...")
    
    # Check mediapipe package directory
    import mediapipe
    mp_path = os.path.dirname(mediapipe.__file__)
    print(f"MediaPipe directory: {mp_path}")
    
    sys.exit(1)
