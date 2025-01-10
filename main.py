from tkinter import *
from tkinter import messagebox
from pygame import mixer
from tkinter.ttk import *
from PIL import Image, ImageTk
import sys
import json
import traceback

import window_manager as manager
import keypress_tracker as tracker
import debug_console as debug
import letter_core as letter
import saving_agent as saving

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
        except Exception as e:
            error_message = traceback.format_exc()
            debug.send(f"Error executing command: {error_message}")
        debug.debug_window.to_execute = ""
    #Updating all windows
    for window_name in manager.registered:
        if window_name == "main":
            if saving.new_language != None:
                manager.window.language_name = saving.new_language
                saving.new_language = None
            if True:#This should look if the editor is in focus
                if manager.editor_selected_label.letter != manager.editor_canvas.letter_name or manager.editor_selected_label.language != manager.window.language_name or manager.editor_selected_label.saved != manager.editor_canvas.saved:
                    manager.txt_selected_label.set(f"Selected: {manager.editor_canvas.letter_name} [{manager.window.language_name}] {"*" if not manager.editor_canvas.saved else ""}")
                    manager.editor_selected_label.letter = manager.editor_canvas.letter_name
                    manager.editor_selected_label.language = manager.window.language_name
                    manager.editor_selected_label.saved = manager.editor_canvas.saved
                if manager.editor_canvas.reload_segments:
                    manager.editor_segment_listbox.delete(0,END)
                    for segment in manager.editor_canvas.letter.segments:
                        manager.editor_segment_listbox.insert(END,segment.name)
                    manager.editor_canvas.reload_segments = False

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