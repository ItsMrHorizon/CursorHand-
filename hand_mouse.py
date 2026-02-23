import cv2
import mediapipe as mp
import pyautogui
import urllib.request
import os
import time
import math  # For distance calculation

# ========================= CONFIGURATION (tune here) =========================
SMOOTHING_ALPHA   = 0.50       # Lower for trackpad-like quick response; range: 0.3–0.7
MOVEMENT_SCALE    = 2.4        # Adjust for full-screen cursor travel
HORIZONTAL_OFFSET = 0.0
VERTICAL_OFFSET   = 0.0
FRAME_SKIP        = 3          # Increase to 4 if FPS remains low (aim for 10–15+ FPS)
CAM_WIDTH         = 480
CAM_HEIGHT        = 360
PERSIST_FRAMES    = 5          # Frames to persist last detection (reduces flicker and improves smoothness)
CLICK_THRESHOLD   = 0.05       # Normalized distance between thumb and index tips for click (tune: 0.03–0.07)
# ============================================================================

# Model download (one-time)
MODEL_URL  = "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task"
MODEL_PATH = "hand_landmarker.task"

if not os.path.exists(MODEL_PATH):
    print("Downloading model (one-time only)...")
    urllib.request.urlretrieve(MODEL_URL, MODEL_PATH)
    print("Download complete.")

# Initialize Hand Landmarker (defaults to CPU)
base_options = mp.tasks.BaseOptions(
    model_asset_path=MODEL_PATH
)
options = mp.tasks.vision.HandLandmarkerOptions(
    base_options=base_options,
    running_mode=mp.tasks.vision.RunningMode.VIDEO,
    num_hands=1,
    min_hand_detection_confidence=0.4,
    min_hand_presence_confidence=0.4,
    min_tracking_confidence=0.4
)
landmarker = mp.tasks.vision.HandLandmarker.create_from_options(options)

# Camera (low resolution for performance)
cam = cv2.VideoCapture(0)
cam.set(cv2.CAP_PROP_FRAME_WIDTH, CAM_WIDTH)
cam.set(cv2.CAP_PROP_FRAME_HEIGHT, CAM_HEIGHT)

screen_w, screen_h = pyautogui.size()

# State variables
smoothed_x = screen_w / 2.0
smoothed_y = screen_h / 2.0
last_target_x = smoothed_x
last_target_y = smoothed_y
frame_count = 0
prev_time = time.time()
missed_frames = 0
last_hand_landmarks = None
was_pinched = False  # Debounce for click detection

# Hand connections for wireframe
HAND_CONNECTIONS = [
    (0,1),(1,2),(2,3),(3,4),      # thumb
    (5,6),(6,7),(7,8),            # index
    (9,10),(10,11),(11,12),       # middle
    (13,14),(14,15),(15,16),      # ring
    (17,18),(18,19),(19,20),      # pinky
    (0,5),(5,9),(9,13),(13,17),(0,17)  # palm
]

def draw_landmarks(image, landmarks):
    h, w, _ = image.shape
    pts = [(int(lm.x * w), int(lm.y * h)) for lm in landmarks]
    for pt in pts:
        cv2.circle(image, pt, 4, (0, 255, 0), -1)  # Green landmarks
    for conn in HAND_CONNECTIONS:
        cv2.line(image, pts[conn[0]], pts[conn[1]], (255, 255, 255), 2)  # White connections

# Eliminate PyAutoGUI delays for smoother cursor movement
pyautogui.PAUSE = 0

print("=== Modern Tasks API Hand Mouse (with Pinch-to-Click) ===")
print("Move index finger for cursor. Pinch thumb and index for click. Press 'q' to quit.")

while True:
    success, frame = cam.read()
    if not success:
        break

    frame = cv2.flip(frame, 1)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)

    frame_count += 1
    timestamp_ms = int(time.time() * 1000)

    hand_detected = False
    if frame_count % FRAME_SKIP == 0:
        results = landmarker.detect_for_video(mp_image, timestamp_ms)
        if results and results.hand_landmarks:
            hand_detected = True
            last_hand_landmarks = results.hand_landmarks[0]
            missed_frames = 0

            # Index fingertip (landmark 8)
            index_tip = last_hand_landmarks[8]

            # Map to screen
            target_x = screen_w * (HORIZONTAL_OFFSET + MOVEMENT_SCALE * index_tip.x)
            target_y = screen_h * (VERTICAL_OFFSET + MOVEMENT_SCALE * index_tip.y)
            target_x = max(10, min(screen_w - 10, target_x))
            target_y = max(10, min(screen_h - 10, target_y))

            last_target_x = target_x
            last_target_y = target_y

            # Click detection: Distance between thumb tip (4) and index tip (8)
            thumb_tip = last_hand_landmarks[4]
            distance = math.sqrt(
                (index_tip.x - thumb_tip.x) ** 2 +
                (index_tip.y - thumb_tip.y) ** 2 +
                (index_tip.z - thumb_tip.z) ** 2  # Include Z for depth accuracy
            )
            is_pinched = distance < CLICK_THRESHOLD

            if is_pinched and not was_pinched:
                pyautogui.click()  # Simulate left-click
            was_pinched = is_pinched

    # Persistence logic to reduce flicker and maintain smooth cursor
    if not hand_detected:
        missed_frames += 1
        if missed_frames <= PERSIST_FRAMES and last_hand_landmarks:
            hand_detected = True  # Simulate detection for persistence

    # Draw wireframe if detected (or persisted)
    if hand_detected and last_hand_landmarks:
        draw_landmarks(frame, last_hand_landmarks)

        # Highlight index tip
        h, w, _ = frame.shape
        tip_x = int(last_hand_landmarks[8].x * w)
        tip_y = int(last_hand_landmarks[8].y * h)
        cv2.circle(frame, (tip_x, tip_y), 12, (0, 0, 255), -1)

    # Always smooth and move cursor (enhanced for trackpad-like response)
    smoothed_x = SMOOTHING_ALPHA * smoothed_x + (1 - SMOOTHING_ALPHA) * last_target_x
    smoothed_y = SMOOTHING_ALPHA * smoothed_y + (1 - SMOOTHING_ALPHA) * last_target_y
    pyautogui.moveTo(smoothed_x, smoothed_y)

    # Status & FPS display
    status = "✅ Hand OK - Move index finger" if hand_detected else "❌ Show hand (palm facing camera)"
    cv2.putText(frame, status, (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 255, 0) if hand_detected else (0, 0, 255), 2)
    fps = 1 / (time.time() - prev_time + 1e-8)
    prev_time = time.time()
    cv2.putText(frame, f"FPS: {fps:.1f}", (20, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)

    cv2.imshow('Modern Hand Mouse', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cam.release()
cv2.destroyAllWindows()
print("Script stopped.")