# gui.py
import tkinter as tk
import asyncio
from PIL import Image, ImageTk
from websocket_handler import publish_message

def update_video_feed(video_label, image):
    """ Updates the video feed in the GUI. """
    from PIL import Image, ImageTk
    image = Image.fromarray(image)
    imgtk = ImageTk.PhotoImage(image=image)
    video_label.imgtk = imgtk
    video_label.configure(image=imgtk)

def update_response_listbox(response_listbox, text):
    """ Updates the response listbox with new messages. """
    response_listbox.insert(tk.END, text)
    response_listbox.yview(tk.END)

def update_detected_items(detected_items_listbox, detected_items):
    """ Updates the detected objects listbox. """
    detected_items_listbox.delete(0, tk.END)
    for item in detected_items:
        detected_items_listbox.insert(tk.END, item)

def run_publish_button(action, user_input_box):
    """ Runs the publish function asynchronously. """
    user_text = user_input_box.get().strip()
    if not user_text and action in ["say", "ask", "llm"]:
        print("No text entered.")
        return
    asyncio.create_task(publish_message(action, user_text))

def update_video_feed(video_label, image, detections, face_detected, is_smiling, is_sad, hand_detected, raised_hand, raised_hand_label, face_label):
    """ Updates the video feed and GUI labels. """

    # ✅ GUI Updates for Hand Detection
    if raised_hand:
        raised_hand_label.config(text="Raised Hand Detected ✅", fg="green")
    elif hand_detected:
        raised_hand_label.config(text="Hand Detected ✋", fg="orange")
    else:
        raised_hand_label.config(text="No Hand ❌", fg="red")

    # ✅ GUI Updates for Face Detection
    if is_smiling:
        face_label.config(text="Smiling Face 😊", fg="green")
    elif is_sad:
        face_label.config(text="Sad Face 😞", fg="blue")
    elif face_detected:
        face_label.config(text="Face Detected 😐", fg="orange")
    else:
        face_label.config(text="No Face ❌", fg="red")

    # ✅ Convert Image for Tkinter Display
    image = Image.fromarray(image)
    imgtk = ImageTk.PhotoImage(image=image)
    video_label.imgtk = imgtk
    video_label.configure(image=imgtk)

def start_gui():
    """ Sets up and starts the Tkinter GUI. """
    root = tk.Tk()
    root.title("WebSocket Video Feed with Face & Hand Detection")

    video_label = tk.Label(root)
    video_label.grid(row=0, column=0, columnspan=2, padx=10, pady=10)

    frame_lists = tk.Frame(root)
    frame_lists.grid(row=1, column=0, columnspan=2, padx=10, pady=5)

    raised_hand_label = tk.Label(frame_lists, text="No Hand ❌", font=("Arial", 14), fg="red")
    raised_hand_label.grid(row=0, column=0)

    face_label = tk.Label(frame_lists, text="No Face ❌", font=("Arial", 14), fg="red")
    face_label.grid(row=0, column=1)

    response_label = tk.Label(root, text="Responses", font=("Arial", 12, "bold"))
    response_label.grid(row=2, column=1, padx=10, pady=5)

    response_listbox = tk.Listbox(root, height=5, width=50)
    response_listbox.grid(row=3, column=1, padx=10, pady=5)

    detected_label = tk.Label(root, text="Detected Objects", font=("Arial", 12, "bold"))
    detected_label.grid(row=2, column=0, padx=10, pady=5)

    detected_items_listbox = tk.Listbox(root, height=5, width=50)
    detected_items_listbox.grid(row=3, column=0, padx=10, pady=5)

    user_input_box = tk.Entry(root, width=50)
    user_input_box.grid(row=4, column=0, columnspan=2, padx=10, pady=5)

    button_frame = tk.Frame(root)
    button_frame.grid(row=5, column=0, columnspan=2)

    buttons = [
        ("Say", "say"), ("Ask", "ask"), ("LLM", "llm"),
        ("Start Recording", "start"), ("Stop Recording", "stop")
    ]

    for i, (label, action) in enumerate(buttons):
        tk.Button(button_frame, text=label, command=lambda a=action: asyncio.create_task(publish_message(a, user_input_box.get().strip()))).grid(row=0, column=i, padx=5)

    root.protocol("WM_DELETE_WINDOW", root.quit)

    # ✅ Return GUI + update functions
    return root, video_label, detected_items_listbox, response_listbox, raised_hand_label, face_label, update_video_feed, update_detected_items, update_response_listbox