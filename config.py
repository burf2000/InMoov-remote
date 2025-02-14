# config.py
import mediapipe as mp
from ultralytics import YOLO

# WebSocket server URL
URI = "ws://127.0.0.1:8888/api/messages"
#URI = "ws://192.168.0.100:8080/api/messages"

# YOLO Model
MODEL = YOLO("yolov8n.pt")

# Mediapipe Hand Tracking
MP_HANDS = mp.solutions.hands
HANDS = MP_HANDS.Hands(min_detection_confidence=0.4, min_tracking_confidence=0.4)
MP_DRAWING = mp.solutions.drawing_utils

# Mediapipe Face Mesh
MP_FACE_MESH = mp.solutions.face_mesh
FACE_MESH = MP_FACE_MESH.FaceMesh(min_detection_confidence=0.5, min_tracking_confidence=0.5)

# Global Variables
websocket = None
running = True