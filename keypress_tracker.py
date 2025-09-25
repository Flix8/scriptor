import sys
from collections import deque

#COMPLETELY WRITTEN BY AI
#What this does: Tracking any keyboard input and sending it back to the rest of the program.

MAX_KEYS_TO_TRACK = 10
keypress_history = deque(maxlen=MAX_KEYS_TO_TRACK)

if sys.platform == "win32":
    import keyboard

    WINDOWS_KEY_TRANSLATIONS = {
        "umschalt": "shift",
        "strg": "ctrl",
    }

    def track_keypress(event):
        if event.device is None:
            key_name = WINDOWS_KEY_TRANSLATIONS.get(event.name.lower(), event.name.lower())
            key_event = (event.event_type, key_name)
            keypress_history.append(key_event)

    keyboard.hook(track_keypress)

elif sys.platform == "darwin":
    from pynput import keyboard

    # Special key mapping for macOS (pynput `Key` → Standard name)
    MACOS_KEY_MAPPING = {
        keyboard.Key.shift: "shift",
        keyboard.Key.ctrl: "ctrl",
        keyboard.Key.alt: "alt",
        keyboard.Key.cmd: "cmd",
        keyboard.Key.enter: "enter",
        keyboard.Key.space: "space",
        keyboard.Key.backspace: "backspace",
        keyboard.Key.tab: "tab",
        keyboard.Key.esc: "esc",
        keyboard.Key.up: "up",
        keyboard.Key.down: "down",
        keyboard.Key.left: "left",
        keyboard.Key.right: "right",
    }
    
    for i in range(1, 13):
        MACOS_KEY_MAPPING[getattr(keyboard.Key, f"f{i}", None)] = f"f{i}"

    def on_press(key):
        key_name = MACOS_KEY_MAPPING.get(key, str(key).strip("'"))  # Convert `Key.shift` → `"shift"`
        keypress_history.append(("down", key_name))

    def on_release(key):
        key_name = MACOS_KEY_MAPPING.get(key, str(key).strip("'"))
        keypress_history.append(("up", key_name))

    listener = keyboard.Listener(on_press=on_press, on_release=on_release)
    listener.start()