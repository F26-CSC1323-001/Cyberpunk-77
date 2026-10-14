
import cv2
import mediapipe as mp
import time
from collections import deque

# ==========================================
# MUSIC SWIPER - HAND GESTURE DETECTION
# ==========================================

MODEL_PATH = "hand_landmarker.task"

# Swipe settings
SWIPE_DISTANCE = 0.10
SWIPE_MIN_TIME = 0.15
SWIPE_MAX_TIME = 1.20
SWIPE_COOLDOWN = 1.0

# Open palm pause settings
PALM_HOLD_TIME = 1.2

# ==========================================
# MEDIAPIPE SETUP
# ==========================================

BaseOptions = mp.tasks.BaseOptions
HandLandmarker = mp.tasks.vision.HandLandmarker
HandLandmarkerOptions = mp.tasks.vision.HandLandmarkerOptions
VisionRunningMode = mp.tasks.vision.RunningMode

options = HandLandmarkerOptions(
    base_options=BaseOptions(model_asset_path=MODEL_PATH),
    running_mode=VisionRunningMode.VIDEO,
    num_hands=1
)

connections = (
    mp.tasks.vision.HandLandmarksConnections.HAND_CONNECTIONS
)

# ==========================================
# HELPER FUNCTIONS
# ==========================================

def finger_is_up(landmarks, tip, joint):
    return landmarks[tip].y < landmarks[joint].y


def is_open_palm(landmarks):
    index_up = finger_is_up(landmarks, 8, 6)
    middle_up = finger_is_up(landmarks, 12, 10)
    ring_up = finger_is_up(landmarks, 16, 14)
    pinky_up = finger_is_up(landmarks, 20, 18)

    return index_up and middle_up and ring_up and pinky_up


def get_palm_center(landmarks):
    # Average the wrist and four palm knuckles
    palm_points = [0, 5, 9, 13, 17]

    center_x = sum(
        landmarks[i].x for i in palm_points
    ) / len(palm_points)

    center_y = sum(
        landmarks[i].y for i in palm_points
    ) / len(palm_points)

    return center_x, center_y


# ==========================================
# CAMERA SETUP
# ==========================================

# Camera 0 for now; we can select your USB camera later.
camera = cv2.VideoCapture(0, cv2.CAP_DSHOW)

if not camera.isOpened():
    print("ERROR: Could not open camera.")
    raise SystemExit

# ==========================================
# GESTURE VARIABLES
# ==========================================

# Stores (time, palm_x, palm_y)
positions = deque()

last_swipe_time = 0
palm_start_time = None
palm_triggered = False

current_action = "Show your hand"
action_time = 0
previous_timestamp_ms = 0

# ==========================================
# MAIN PROGRAM
# ==========================================

try:
    with HandLandmarker.create_from_options(options) as landmarker:

        while True:
            success, frame = camera.read()

            if not success:
                print("ERROR: Could not read from camera.")
                break

            # Mirror the image
            frame = cv2.flip(frame, 1)

            height, width, _ = frame.shape
            now = time.time()

            # Convert image to RGB for MediaPipe
            rgb_frame = cv2.cvtColor(
                frame, cv2.COLOR_BGR2RGB
            )

            mp_image = mp.Image(
                image_format=mp.ImageFormat.SRGB,
                data=rgb_frame
            )

            # Use increasing timestamps for VIDEO mode
            timestamp_ms = max(
                int(now * 1000),
                previous_timestamp_ms + 1
            )
            previous_timestamp_ms = timestamp_ms

            result = landmarker.detect_for_video(
                mp_image, timestamp_ms
            )

            hand_detected = False
            movement_text = "Palm movement: --"

            # ==================================
            # HAND TRACKING
            # ==================================

            if result.hand_landmarks:
                hand_detected = True
                landmarks = result.hand_landmarks[0]

                # Draw the 21 landmark dots
                points = []

                for landmark in landmarks:
                    x = int(landmark.x * width)
                    y = int(landmark.y * height)

                    points.append((x, y))

                    cv2.circle(
                        frame, (x, y), 5, (0, 255, 0), -1
                    )

                # Draw connections between landmarks
                for connection in connections:
                    start = points[connection.start]
                    end = points[connection.end]

                    cv2.line(
                        frame, start, end, (255, 0, 0), 2
                    )

                # Calculate the center of the palm
                center_x, center_y = get_palm_center(landmarks)

                # Mark the palm center
                palm_pixel_x = int(center_x * width)
                palm_pixel_y = int(center_y * height)

                cv2.circle(
                    frame,
                    (palm_pixel_x, palm_pixel_y),
                    9,
                    (0, 0, 255),
                    -1
                )

                # Store current palm position
                positions.append(
                    (now, center_x, center_y)
                )

                # Keep only the last 1.2 seconds
                while (
                    positions
                    and now - positions[0][0] > SWIPE_MAX_TIME
                ):
                    positions.popleft()

                # ==================================
                # OPEN PALM = PAUSE
                # ==================================

                open_palm = is_open_palm(landmarks)

                if open_palm:
                    if palm_start_time is None:
                        palm_start_time = now

                    held_time = now - palm_start_time

                    if held_time >= PALM_HOLD_TIME:
                        if not palm_triggered:
                            current_action = "PAUSE MUSIC"
                            action_time = now
                            palm_triggered = True
                    else:
                        current_action = (
                            f"Hold palm: {held_time:.1f}s"
                        )

                else:
                    palm_start_time = None
                    palm_triggered = False

                    # ==================================
                    # SWIPE LEFT / RIGHT
                    # ==================================

                    if len(positions) >= 2:
                        old_time, old_x, old_y = positions[0]
                        elapsed = now - old_time

                        dx = center_x - old_x
                        dy = center_y - old_y

                        movement_text = (
                            f"Palm movement: {dx:+.3f}"
                        )

                        if (
                            SWIPE_MIN_TIME <= elapsed <= SWIPE_MAX_TIME
                            and abs(dx) >= SWIPE_DISTANCE
                            and abs(dx) > abs(dy) * 1.2
                            and now - last_swipe_time >= SWIPE_COOLDOWN
                        ):
                            if dx > 0:
                                current_action = "NEXT SONG"
                            else:
                                current_action = "PREVIOUS SONG"

                            action_time = now
                            last_swipe_time = now

                            # Clear movement history after a swipe
                            positions.clear()

            else:
                positions.clear()
                palm_start_time = None
                palm_triggered = False

            # ==================================
            # DISPLAY COMMANDS AND DEBUG INFO
            # ==================================

            if now - action_time > 2.0:
                if hand_detected:
                    current_action = "Tracking hand"
                else:
                    current_action = "No hand detected"

            cv2.putText(
                frame,
                current_action,
                (20, 45),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.9,
                (0, 255, 0),
                2
            )

            cv2.putText(
                frame,
                movement_text,
                (20, 80),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 255, 255),
                2
            )

            cv2.putText(
                frame,
                "Swipe RIGHT = Next song",
                (20, height - 65),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (255, 255, 255),
                2
            )

            cv2.putText(
                frame,
                "Swipe LEFT = Previous song",
                (20, height - 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (255, 255, 255),
                2
            )

            cv2.putText(
                frame,
                "Hold OPEN PALM = Pause | Q = Quit",
                (20, height - 15),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (255, 255, 255),
                2
            )

            cv2.imshow(
                "Music Swiper - Hand Tracking", frame
            )

            # Press Q to quit
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

finally:
    camera.release()
    cv2.destroyAllWindows()

print("Music Swiper stopped.")
