# main.py
import asyncio
from gui import start_gui
from websocket_handler import subscribe_to_channel
from mrl_models import get_inmoov2_instance

async def main():
    """ Main function to run both the Tkinter GUI and the WebSocket communication. """
    root, video_label, detected_items_listbox, response_listbox, raised_hand_label, face_label, update_video_feed, update_detected_items, update_response_listbox = start_gui()

    # ✅ Now correctly passing function references
    asyncio.create_task(subscribe_to_channel(
        video_label,
        detected_items_listbox,
        response_listbox,
        raised_hand_label,  # ✅ Passed now
        face_label,  # ✅ Passed now
        update_video_feed,
        update_detected_items,
        update_response_listbox
    ))

    # Keep Tkinter running in the asyncio event loop
    while True:
        root.update_idletasks()
        root.update()
        await asyncio.sleep(0.01)  # Allow asyncio to run

if __name__ == "__main__":

    inmoov = get_inmoov2_instance()
    if inmoov:
        print(f"InMoov2 Service Name: {inmoov.name}")
        print(f"Running Status: {inmoov.isRunning}")
        print(f"Number of Peers: {len(inmoov.config.peers)}")
        print("List of Gestures:", ", ".join(inmoov.get_gestures()))


    asyncio.run(main())