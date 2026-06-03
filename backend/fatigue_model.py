import cv2
import numpy as np
from collections import deque
from time import time


class FatigueDetector:
    """
    Real-time fatigue detection using OpenCV Haar Cascades and Eye Aspect Ratio (EAR).
    Uses OpenCV's built-in face and eye detection for reliability without external model dependencies.
    """

    # EAR threshold for detecting closed eyes
    EAR_THRESHOLD = 0.25

    # Frame threshold for prolonged eye closure
    CLOSED_FRAME_THRESHOLD = 20

    def __init__(self):
        """Initialize OpenCV Haar Cascades and detection parameters."""
        # Load Haar Cascade classifiers
        cascade_path = cv2.data.haarcascades
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )
        self.eye_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_eye.xml'
        )

        # Detection state
        self.closed_frames = 0
        self.blink_count = 0
        self.blink_times = deque(maxlen=30)  # Store last 30 seconds of blink timestamps
        self.fatigue_score = 0
        self.status = "Awake"
        self.current_ear = 0.0
        self.face_detected = False

        # Timing
        self.start_time = time()
        self.last_blink_time = time()
        self.last_status = "Awake"

    def calculate_ear(self, eye_region):
        """
        Calculate Eye Aspect Ratio (EAR) from eye region.
        Uses the contour of the detected eye.
        """
        if eye_region.size == 0:
            return 0.0
        
        # Convert to grayscale
        gray = cv2.cvtColor(eye_region, cv2.COLOR_BGR2GRAY)
        
        # Apply threshold to get binary image
        _, binary = cv2.threshold(gray, 40, 255, cv2.THRESH_BINARY_INV)
        
        # Find contours
        contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if not contours:
            return 0.5  # Default: eye open
        
        # Get the largest contour (the eye)
        largest_contour = max(contours, key=cv2.contourArea)
        area = cv2.contourArea(largest_contour)
        
        # Get bounding rectangle
        x, y, w, h = cv2.boundingRect(largest_contour)
        
        # Calculate aspect ratio
        if w == 0:
            return 0.5
        
        aspect_ratio = h / w if w > 0 else 0
        
        # Normalize EAR: lower ratio = more closed
        # Map from typical range [0.1, 0.5] to [0.1, 0.5]
        ear = max(0, min(1, aspect_ratio))
        
        return ear

    def process_frame(self, frame):
        """
        Process a single frame for fatigue detection.

        Args:
            frame: Input frame from webcam (BGR format)

        Returns:
            tuple: (annotated_frame, stats_dict)
                - annotated_frame: Frame with drawn landmarks and status
                - stats_dict: Dictionary with detection metrics
        """
        height, width, _ = frame.shape
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        annotated_frame = frame.copy()

        self.face_detected = False
        eyes_closed = False
        ear_left = 0.0
        ear_right = 0.0

        # Detect faces
        faces = self.face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

        if len(faces) > 0:
            self.face_detected = True
            # Use the largest face detected
            face = max(faces, key=lambda f: f[2] * f[3])
            x, y, w, h = face

            # Extract face region
            face_roi = gray[y:y+h, x:x+w]
            face_roi_color = frame[y:y+h, x:x+w]

            # Detect eyes in face region
            eyes = self.eye_cascade.detectMultiScale(face_roi, scaleFactor=1.1, minNeighbors=10, minSize=(15, 15))

            if len(eyes) >= 2:
                # Sort eyes left to right
                eyes = sorted(eyes, key=lambda e: e[0])
                
                # Process left eye
                ex1, ey1, ew1, eh1 = eyes[0]
                left_eye_roi = face_roi_color[ey1:ey1+eh1, ex1:ex1+ew1]
                ear_left = self.calculate_ear(left_eye_roi)
                
                # Draw left eye circle
                cv2.circle(annotated_frame, (x + ex1 + ew1//2, y + ey1 + eh1//2), 5, (0, 255, 180), -1)

                # Process right eye
                if len(eyes) > 1:
                    ex2, ey2, ew2, eh2 = eyes[1]
                    right_eye_roi = face_roi_color[ey2:ey2+eh2, ex2:ex2+ew2]
                    ear_right = self.calculate_ear(right_eye_roi)
                    
                    # Draw right eye circle
                    cv2.circle(annotated_frame, (x + ex2 + ew2//2, y + ey2 + eh2//2), 5, (0, 255, 180), -1)
                else:
                    ear_right = ear_left

            self.current_ear = (ear_left + ear_right) / 2.0

            # Check if eyes are closed
            if self.current_ear < self.EAR_THRESHOLD:
                eyes_closed = True
                self.closed_frames += 1
            else:
                # Eyes are open
                if self.closed_frames > 0:
                    # Just transitioned from closed to open -> register blink
                    if self.closed_frames < 10:  # Filter out very long closures (not blinks)
                        self.blink_count += 1
                        self.blink_times.append(time())

                self.closed_frames = 0

            # Draw face rectangle
            cv2.rectangle(annotated_frame, (x, y), (x+w, y+h), (0, 255, 180), 2)

        # Update fatigue score
        current_time = time()
        elapsed_time = current_time - self.start_time

        if self.face_detected:
            # Prolonged eye closure increases fatigue
            if self.closed_frames >= self.CLOSED_FRAME_THRESHOLD:
                self.fatigue_score = min(100, self.fatigue_score + 3)
            else:
                # Low blink rate check (after 10 seconds)
                if elapsed_time > 10:
                    blink_rate = self.get_blink_rate()
                    if blink_rate < 15:
                        self.fatigue_score = min(100, self.fatigue_score + 1)

                # Normal state decreases fatigue slowly
                self.fatigue_score = max(0, self.fatigue_score - 1)
        else:
            # No face detected -> increase fatigue score (can't monitor)
            self.fatigue_score = min(100, self.fatigue_score + 2)

        # Update status based on fatigue score
        if self.fatigue_score < 40:
            self.status = "Awake"
        elif self.fatigue_score < 70:
            self.status = "Tired"
        else:
            self.status = "DROWSY"

        # Draw status, EAR, blink rate, and fatigue percentage on frame
        status_color = (0, 255, 0) if self.status == "Awake" else (0, 165, 255) if self.status == "Tired" else (0, 0, 255)

        cv2.putText(annotated_frame, f"Status: {self.status}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, status_color, 2)
        cv2.putText(annotated_frame, f"EAR: {self.current_ear:.2f}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
        cv2.putText(annotated_frame, f"Blinks/min: {self.get_blink_rate():.1f}", (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
        cv2.putText(annotated_frame, f"Fatigue: {self.fatigue_score}%", (10, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)

        # Draw red rectangle border when drowsy
        if self.status == "DROWSY":
            cv2.rectangle(annotated_frame, (5, 5), (width - 5, height - 5), (0, 0, 255), 3)

        # Prepare stats dictionary
        stats = {
            "face_detected": self.face_detected,
            "status": self.status,
            "fatigue_score": self.fatigue_score,
            "ear": round(self.current_ear, 3),
            "blink_rate": round(self.get_blink_rate(), 1),
            "blink_count": self.blink_count,
            "closed_frames": self.closed_frames,
            "timestamp": current_time
        }

        return annotated_frame, stats

    def get_blink_rate(self):
        """
        Calculate blink rate (blinks per minute) based on last 30 seconds.
        """
        current_time = time()
        cutoff_time = current_time - 30  # Last 30 seconds

        # Count blinks in the last 30 seconds
        recent_blinks = sum(1 for t in self.blink_times if t > cutoff_time)

        # Calculate blinks per minute
        if len(self.blink_times) > 0:
            time_span = current_time - self.blink_times[0]
            if time_span > 0:
                return (recent_blinks / time_span) * 60
        return 0.0

    def reset(self):
        """Reset detector to initial state."""
        self.closed_frames = 0
        self.blink_count = 0
        self.blink_times.clear()
        self.fatigue_score = 0
        self.status = "Awake"
        self.current_ear = 0.0
        self.start_time = time()
        self.last_status = "Awake"
