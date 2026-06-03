import cv2
import numpy as np
from collections import deque
from time import time

try:
    import mediapipe as mp
    from mediapipe.tasks.python import vision
    from mediapipe.framework.formats import landmark_pb2
except ImportError:
    # Fallback for different MediaPipe versions
    import mediapipe as mp


class FatigueDetector:
    """
    Real-time fatigue detection using MediaPipe Face Mesh and Eye Aspect Ratio (EAR).
    """

    # Eye landmark indices from MediaPipe Face Mesh
    LEFT_EYE = [33, 160, 158, 133, 153, 144]
    RIGHT_EYE = [362, 385, 387, 263, 373, 380]

    # EAR threshold for detecting closed eyes
    EAR_THRESHOLD = 0.25

    # Frame threshold for prolonged eye closure
    CLOSED_FRAME_THRESHOLD = 20

    def __init__(self):
        """Initialize MediaPipe Face Mesh and detection parameters."""
        try:
            # Try legacy API first (mp.solutions)
            self.face_mesh = mp.solutions.face_mesh.FaceMesh(
                max_num_faces=1,
                refine_landmarks=True,
                min_detection_confidence=0.5,
                min_tracking_confidence=0.5
            )
        except AttributeError:
            # If solutions not available, try direct import
            from mediapipe.solutions import face_mesh as face_mesh_module
            self.face_mesh = face_mesh_module.FaceMesh(
                max_num_faces=1,
                refine_landmarks=True,
                min_detection_confidence=0.5,
                min_tracking_confidence=0.5
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

    def calculate_ear(self, eye_landmarks):
        """
        Calculate Eye Aspect Ratio (EAR).
        EAR = (|p2-p6| + |p3-p5|) / (2 * |p1-p4|)
        where p1-p6 are the eye landmarks in order.
        """
        # Calculate vertical distances
        vertical_1 = np.linalg.norm(eye_landmarks[1] - eye_landmarks[5])
        vertical_2 = np.linalg.norm(eye_landmarks[2] - eye_landmarks[4])

        # Calculate horizontal distance
        horizontal = np.linalg.norm(eye_landmarks[0] - eye_landmarks[3])

        # Calculate EAR
        ear = (vertical_1 + vertical_2) / (2 * horizontal + 1e-6)
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
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Run face mesh detection
        results = self.face_mesh.process(rgb_frame)
        annotated_frame = frame.copy()

        self.face_detected = False
        eyes_closed = False

        if results.multi_face_landmarks:
            self.face_detected = True
            landmarks = results.multi_face_landmarks[0].landmark

            # Extract eye landmarks in normalized coordinates
            left_eye = np.array([[landmarks[i].x * width, landmarks[i].y * height] for i in self.LEFT_EYE])
            right_eye = np.array([[landmarks[i].x * width, landmarks[i].y * height] for i in self.RIGHT_EYE])

            # Calculate EAR for both eyes
            left_ear = self.calculate_ear(left_eye)
            right_ear = self.calculate_ear(right_eye)
            self.current_ear = (left_ear + right_ear) / 2.0

            # Draw eye landmarks (cyan dots)
            eye_color = (0, 255, 180)
            for eye_points in [left_eye, right_eye]:
                for point in eye_points:
                    cv2.circle(annotated_frame, tuple(map(int, point)), 2, eye_color, -1)

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
