from tkinter import *
from tkinter import messagebox
from pygame import mixer
from tkinter.ttk import *
from PIL import Image, ImageTk
import sys

import window_manager as manager
import keypress_tracker as tracker
import debug_console as debug
import letter_core as letter

def custom_handler(exc_type, exc_value, exc_traceback):
    on_exit()
    if exc_type != KeyboardInterrupt:
        messagebox.showerror("ERROR",f"A fatal error occured: {exc_type,exc_value}")
    sys.__excepthook__(exc_type, exc_value, exc_traceback)
#DEBUG
debug_mode = False
def flick_debug():
    global debug_mode
    debug_mode = not debug_mode
    if debug_mode:
        debug.root.deiconify()
        debug.debug_window.command_entry.focus()
    else:
        debug.root.withdraw()

def manual_exit():
    if debug_mode:
        on_exit()

def on_update():
    #Process keys
    if 'f8' in tracker.keypress_history:
        flick_debug()
    if 'esc' in tracker.keypress_history:
        manual_exit()
    tracker.keypress_history.clear()
    #Executing command in console
    if debug.debug_window.to_execute != "":
        try:
            exec(debug.debug_window.to_execute,globals())
        except:
            debug.send("Error executing command!")
        debug.debug_window.to_execute = ""
    #Updating all windows
    for window_name in manager.registered:
        pass

    manager.get("main").after(100,on_update)
def on_exit():
    for window_name in manager.registered:
        if window_name == "Main": continue
        try:
            manager.registered[window_name].destroy()
        except TclError:
            pass
    manager.get("main").destroy()

manager.get("main").protocol("WM_DELETE_WINDOW", on_exit)
manager.get("main").after(0,on_update)

# Set the custom hook
sys.excepthook = custom_handler

manager.get("main").mainloop()