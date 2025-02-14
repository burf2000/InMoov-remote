
import json
import cv2
import websockets
import numpy as np
from ultralytics import YOLO
import mediapipe as mp
from opencv_utils import decode_frame, run_yolo, run_mediapipe_face_detection, run_mediapipe_hand_tracking
from config import URI

websocket = None
# Hack to skip every other frame
skip = False

async def subscribe_to_channel(video_label, detected_items_listbox, response_listbox, raised_hand_label, face_label, update_video_feed, update_detected_items, update_response_listbox):
    """ Handles WebSocket subscription and processes incoming messages. """
    global websocket
    global skip

    try:
        websocket = await websockets.connect(URI, ping_interval=None, max_size=None, compression="deflate")
        print("Connected to WebSocket server.")

        while True:
            message = await websocket.recv()
            if message != "X":
                msg = json.loads(message)

                # Process different types of messages
                if msg.get("method") == "onUtterance":
                    utterance_text = json.loads(msg.get('data')[0]).get('text')
                    print(f"onUtterance: {utterance_text}")
                    update_response_listbox(response_listbox, f"onUtterance: {utterance_text}")

                if msg.get("method") == "onText":
                    text_message = json.loads(msg.get('data')[0])
                    print(f"onText: sender:{msg.get("sender")}  {text_message}")

                    if "htmlFilter" in msg.get("sender", ""):
                        update_response_listbox(response_listbox, f"onText: {text_message}")
                
                if msg.get("method") == "onResponse":
                    response_text = json.loads(msg.get('data')[0])
                    print(f"onResponse: {response_text}")
                    update_response_listbox(response_listbox, f"onResponse: {response_text}")

                if msg.get("method") == "onRequest":
                    request_text = json.loads(msg.get('data')[0])
                    print(f"onRequest: {request_text}")
                    update_response_listbox(response_listbox, f"onRequest: {request_text}")

                if msg.get("method") == "onListeningEvent":
                    listening_text = json.loads(msg.get('data')[0]).get('text')
                    print(f"onListeningEvent: {listening_text}")
                    #update_response_listbox(response_listbox, f"onListeningEvent: {listening_text}")

                if msg.get("method") != "onWebDisplay":
                    print(f"Received method: {msg.get('method')}")

                # Handle image stream from WebSocket
                if msg.get("method") == "onWebDisplay":
                    
                    frame_data = json.loads(msg.get("data")[0]).get("data").replace("data:image/jpg;base64,", "")

                    skip = not skip

                    if skip == False: 
                        image = decode_frame(frame_data)

                        # ✅ Process with YOLO & Mediapipe
                        detections = run_yolo(image)

                        # Draw the boxes
                        # Use YOLOv8 for object detection
                        for detection in detections:
                            x1, y1, x2, y2 = detection["bbox"]
                            label = detection["label"]
                            confidence = detection["confidence"]

                            # Draw bounding boxes for all detected objects
                            cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)

                            # Draw labels
                            label_text = f"{label} ({confidence:.2f})"
                            cv2.putText(image, label_text, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

                        face_detected, is_smiling, is_sad, image = run_mediapipe_face_detection(image)
                        hand_detected, raised_hand, image = run_mediapipe_hand_tracking(image)

                        # ✅ Call `update_video_feed` correctly
                        update_video_feed(video_label, image, detections, face_detected, is_smiling, is_sad, hand_detected, raised_hand, raised_hand_label, face_label)

                        detected_items = [f"{det['label']} ({det['confidence']:.2f})" for det in detections]
                        update_detected_items(detected_items_listbox, detected_items)


    except Exception as e:
        print(f"WebSocket error: {e}")


async def publish_message(message_type, user_text):
    """ Publishes a message to the WebSocket server. """
    global websocket
    if websocket is None:
        print("WebSocket not connected!")
        return

    try:
        if message_type == "say":
            publish_message = json.dumps({
                "name": "i01.chatBot",
                "method": "publishText",
                "data": [json.dumps(user_text)]
            })
        elif message_type == "ask":
            publish_message = json.dumps({
                "name": "i01.chatBot",
                "method": "getResponse",
                "data": [json.dumps(user_text)]
            })
        elif message_type == "llm":
            publish_message = json.dumps({
                "name": "i01.llm",
                "method": "getResponse",
                "data": [json.dumps(user_text)]
            })
        elif message_type == "start":
            publish_message = json.dumps({
                "name": "i01.ear",
                "method": "startRecording"
            })
        elif message_type == "stop":
            publish_message = json.dumps({
                "name": "i01.ear",
                "method": "stopRecording"
            })
        else:
            print("Invalid message type!")
            return

        await websocket.send(publish_message)
        print(f"Published message: {publish_message}")

    except Exception as e:
        print(f"Error while publishing: {e}")