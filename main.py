from tkinter import *
from tkinter import messagebox
from pygame import mixer
from tkinter.ttk import *
from PIL import Image, ImageTk
import sys
import json

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
    if ('down','f8') in tracker.keypress_history:
        flick_debug()
    if ('down','esc') in tracker.keypress_history:
        manual_exit()
    if len(tracker.keypress_history) != 0:
        #Need to send to focused canvas
        manager.editor_canvas.on_key(tracker.keypress_history)
    tracker.keypress_history.clear()
    #Executing command in console
    if debug.debug_window.to_execute != "":
        try:
            if debug.debug_window.to_execute.split(" ")[0] == "get":
                debug.debug_window.to_execute = f"debug.send({debug.debug_window.to_execute.split(" ")[1]})"
            exec(debug.debug_window.to_execute,globals())
        except:
            debug.send("Error executing command!")
        debug.debug_window.to_execute = ""
    #Updating all windows
    for window_name in manager.registered:
        pass

    manager.get("main").after(100,on_update)
def on_exit():
    cmd_log_file = open("debug_cmd_log.json","w")
    json.dump(debug.debug_window.command_log,cmd_log_file,indent=6)
    cmd_log_file.close()
    for window_name in manager.registered:
        if window_name == "main": continue
        try:
            manager.registered[window_name].destroy()
        except TclError:
            pass
    manager.get("main").destroy()

manager.get("main").protocol("WM_DELETE_WINDOW", on_exit)
manager.get("main").after(0,on_update)

# Set the custom hook
sys.excepthook = custom_handler
cmd_log_file = open("debug_cmd_log.json","r")
debug.debug_window.command_log=json.load(cmd_log_file)
cmd_log_file.close()
manager.get("main").mainloop()