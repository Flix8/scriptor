import keyboard
from collections import deque

MAX_KEYS_TO_TRACK = 10

keypress_history = deque(maxlen=MAX_KEYS_TO_TRACK)

def track_keypress(event):
    if  event.device is None:
        key_event = event.event_type,event.name
        keypress_history.append(key_event)
keyboard.hook(track_keypress)
