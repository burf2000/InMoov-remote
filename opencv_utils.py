# opencv_utils.py
import cv2
import base64
import numpy as np
from config import MODEL, HANDS, MP_DRAWING, MP_FACE_MESH, FACE_MESH, MP_HANDS


def decode_frame(frame_data):
    """ Decodes a base64-encoded image frame and resizes it. """
    frame = base64.b64decode(frame_data)
    np_array = np.frombuffer(frame, dtype=np.uint8)
    image = cv2.imdecode(np_array, cv2.IMREAD_COLOR)

    # Resize & Mirror Image
    resized_image = cv2.resize(image, (1024, 768))
    mirrored_image = cv2.flip(resized_image, 1)

    return cv2.cvtColor(mirrored_image, cv2.COLOR_BGR2RGB)


def run_yolo(image):
    """ Runs YOLOv8 on the given image and returns detection results. """
    results = MODEL.predict(image, verbose=False)
    detections = []

    for result in results[0].boxes:
        x1, y1, x2, y2 = map(int, result.xyxy[0])
        class_id = int(result.cls)
        confidence = float(result.conf)
        label = MODEL.names[class_id]

        detections.append({"bbox": (x1, y1, x2, y2), "label": label, "confidence": confidence})

    return detections


def run_mediapipe_face_detection(image):
    """ Detects faces and determines if the person is smiling or sad. """
    face_detected, is_smiling, is_sad = False, False, False
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    results = FACE_MESH.process(image_rgb)

    if results.multi_face_landmarks:
        face_detected = True
        for face_landmarks in results.multi_face_landmarks:
            landmarks = face_landmarks.landmark
            left_mouth = landmarks[61]
            right_mouth = landmarks[291]
            top_mouth = landmarks[13]
            bottom_mouth = landmarks[14]

            mouth_width = abs(right_mouth.x - left_mouth.x)
            mouth_height = abs(bottom_mouth.y - top_mouth.y)
            smile_threshold = mouth_width * 0.25

            if mouth_height > smile_threshold:
                is_smiling = True
            elif mouth_height < smile_threshold * 0.6:
                is_sad = True

            MP_DRAWING.draw_landmarks(image, face_landmarks, MP_FACE_MESH.FACEMESH_TESSELATION)

    return face_detected, is_smiling, is_sad, image


def run_mediapipe_hand_tracking(image):
    """
    Uses Mediapipe to detect hands and determine if a hand is raised.
    Returns:
    - `hand_detected` (bool): Whether a hand is detected.
    - `raised_hand` (bool): Whether a hand is raised.
    - `image`: Image with hand landmarks drawn.
    """
    hand_detected = False
    raised_hand = False

    # Convert image to RGB (Mediapipe expects RGB format)
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    # Process the image with Mediapipe
    results = HANDS.process(image_rgb)

    if results.multi_hand_landmarks:
        hand_detected = True  # ✅ At least one hand detected

        for hand_landmarks in results.multi_hand_landmarks:
            # ✅ Get coordinates for wrist and fingertips
            wrist_y = hand_landmarks.landmark[MP_HANDS.HandLandmark.WRIST].y
            index_finger_tip_y = hand_landmarks.landmark[MP_HANDS.HandLandmark.INDEX_FINGER_TIP].y
            middle_finger_tip_y = hand_landmarks.landmark[MP_HANDS.HandLandmark.MIDDLE_FINGER_TIP].y
            pinky_finger_tip_y = hand_landmarks.landmark[MP_HANDS.HandLandmark.PINKY_TIP].y

            # ✅ Check if fingers are above the wrist
            fingers_above_wrist = sum([
                index_finger_tip_y < wrist_y,
                middle_finger_tip_y < wrist_y,
                pinky_finger_tip_y < wrist_y
            ])

            # ✅ If at least two fingers are raised, classify as a raised hand
            if fingers_above_wrist >= 2:
                raised_hand = True

            # ✅ FIX: Use `mp_hands.HAND_CONNECTIONS` instead of `hands.HAND_CONNECTIONS`
            MP_DRAWING.draw_landmarks(image, hand_landmarks, MP_HANDS.HAND_CONNECTIONS)

    return hand_detected, raised_hand, image