from tkinter import *
from tkinter import messagebox
from tkinter.ttk import *
import sys
import json
import traceback

import window_manager as manager
import keypress_tracker as tracker
import debug_console as debug
import letter_core as letter
import saving_agent as saving
import exporter as export

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
    if ('down','alt') in tracker.keypress_history and ('down','v') in tracker.keypress_history:
        try:
            clipboard = manager.get('main').clipboard_get()
            if clipboard:
                debug.send(f"Executing from clipboard:\n{clipboard}")
                for command in clipboard.split("\n"):
                    debug.debug_window.to_execute.append(command)
        except TclError:
            debug.send("Clipboard empty!")
    if len(tracker.keypress_history) != 0:
        #Need to send to focused canvas
        manager.editor_canvas.on_key(tracker.keypress_history)
        manager.positioning_canvas.on_key(tracker.keypress_history)
    tracker.keypress_history.clear()
    #Executing command in console
    if len(debug.debug_window.to_execute) != 0:
        try:
            for command in debug.debug_window.to_execute:
                if command.split(" ")[0] == "get":
                    command = f"debug.send({command.split(' ')[1]})"
                exec(command,globals())
        except Exception as e:
            error_message = traceback.format_exc()
            debug.send(f"Error executing command: {error_message}")
        debug.debug_window.to_execute.clear()
    #Updating all windows
    for window_name in manager.registered:
        if window_name == "main":
            if saving.new_language != None:
                manager.window.language_name = saving.new_language
                saving.new_language = None
            if manager.window.current_frame == "EDITOR":
                if manager.editor_selected_label.letter != manager.editor_canvas.letter_name or manager.editor_selected_label.language != manager.window.language_name or manager.editor_selected_label.saved != manager.editor_canvas.saved:
                    manager.editor_txt_selected_label.set(f"Selected: {manager.editor_canvas.letter_name} [{manager.window.language_name}] {'*' if not manager.editor_canvas.saved else ''}")
                    manager.editor_selected_label.letter = manager.editor_canvas.letter_name
                    manager.editor_selected_label.language = manager.window.language_name
                    manager.editor_selected_label.saved = manager.editor_canvas.saved
                if manager.editor_canvas.reload_segments:
                    manager.editor_segment_listbox.delete(0,END)
                    for segment in manager.editor_canvas.letter.segments:
                        manager.editor_segment_listbox.insert(END,segment.name)
                    manager.editor_group_listbox.delete(0,END)
                    for group in manager.editor_canvas.letter.groups:
                        manager.editor_group_listbox.insert(END,group)
                    manager.editor_canvas.reload_segments = False
                if isinstance(manager.editor_canvas.configuration_data,list):
                    if manager.editor_canvas.configuration_data[0] == 5:
                        manager.update_inspector_entries(3)
                        manager.inspector_labels_x[2].place_forget()
                        manager.inspector_labels_y[2].place_forget()
                        manager.inspector_entries_y[2].place_forget()
                    else:
                        manager.update_inspector_entries(manager.editor_canvas.configuration_data[0])
                    for i in range(0,(len(manager.editor_canvas.configuration_data)-1)//2):
                        if not manager.editor_canvas.configuration_data[(i+1)*2-1] is None:
                            manager.inspector_vars_x[i].set(manager.editor_canvas.configuration_data[(i+1)*2-1])
                            manager.inspector_entries_x[i].original_value = str(manager.editor_canvas.configuration_data[(i+1)*2-1])
                        if not manager.editor_canvas.configuration_data[(i+1)*2] is None:
                            manager.inspector_vars_y[i].set(manager.editor_canvas.configuration_data[(i+1)*2])
                            manager.inspector_entries_y[i].original_value = str(manager.editor_canvas.configuration_data[(i+1)*2])
                    manager.editor_canvas.configuration_data = None
            elif manager.window.current_frame == "CONFIG":
                if manager.config_selected_label.letter != manager.positioning_canvas.letter_name or manager.config_selected_label.language != manager.window.language_name or manager.config_selected_label.saved != manager.positioning_canvas.saved:
                    manager.config_txt_selected_label.set(f"Selected: {manager.positioning_canvas.letter_name} [{manager.window.language_name}] {'*' if not manager.positioning_canvas.saved else ''}")
                    manager.editor_selected_label.letter = manager.positioning_canvas.letter_name
                    manager.editor_selected_label.language = manager.window.language_name
                    manager.editor_selected_label.saved = manager.positioning_canvas.saved
                if isinstance(manager.positioning_canvas.configuration_data,list):
                    manager.config_update_inspector_entries(manager.positioning_canvas.configuration_data[0])
                    for i in range(0,(len(manager.positioning_canvas.configuration_data)-1)//2):
                        if not manager.positioning_canvas.configuration_data[(i+1)*2-1] is None:
                            manager.config_inspector_vars_x[i].set(manager.positioning_canvas.configuration_data[(i+1)*2-1])
                            manager.config_inspector_entries_x[i].original_value = str(manager.positioning_canvas.configuration_data[(i+1)*2-1])
                        if not manager.positioning_canvas.configuration_data[(i+1)*2] is None:
                            manager.config_inspector_vars_y[i].set(manager.positioning_canvas.configuration_data[(i+1)*2])
                            manager.config_inspector_entries_y[i].original_value = str(manager.positioning_canvas.configuration_data[(i+1)*2])
                    manager.positioning_canvas.configuration_data = None
            elif manager.window.current_frame == "WRITE":
                if manager.write_selected_label.letter != manager.write_canvas.text_name or manager.write_selected_label.language != manager.window.language_name or manager.write_selected_label.saved != manager.write_canvas.saved:
                    manager.write_txt_selected_label.set(f"Selected: {manager.write_canvas.text_name} [{manager.window.language_name}] {'*' if not manager.write_canvas.saved else ''}")
                    manager.write_selected_label.letter = manager.write_canvas.text_name
                    manager.write_selected_label.language = manager.window.language_name
                    manager.write_selected_label.saved = manager.write_canvas.saved
                if manager.write_canvas.reload_slots:
                    #Reload slots
                    manager.write_canvas.reload_slots = False
                if isinstance(manager.write_canvas.configuration_data,list):
                    manager.write_update_inspector_entries(manager.write_canvas.configuration_data[0])
                    for i in range(0,(len(manager.write_canvas.configuration_data)-1)//2):
                        if not manager.write_canvas.configuration_data[(i+1)*2-1] is None:
                            manager.write_inspector_vars_x[i].set(manager.write_canvas.configuration_data[(i+1)*2-1])
                            manager.write_inspector_entries_x[i].original_value = str(manager.write_canvas.configuration_data[(i+1)*2-1])
                        if not manager.write_canvas.configuration_data[(i+1)*2] is None:
                            manager.write_inspector_vars_y[i].set(manager.write_canvas.configuration_data[(i+1)*2])
                            manager.write_inspector_entries_y[i].original_value = str(manager.write_canvas.configuration_data[(i+1)*2])
                    manager.write_canvas.configuration_data = None
    manager.get("main").after(100,on_update)

def on_exit():
    cmd_log_file = open("debug_cmd_log.json","w")
    json.dump(debug.debug_window.command_log,cmd_log_file,indent=6)
    cmd_log_file.close()
    session_save = open("last_session_info.json","w")
    json.dump(saving.SessionData(manager.get("main").language_name,manager.editor_canvas.letter_name,manager.positioning_canvas.letter_name,manager.window.current_frame),session_save,default=lambda o: o.__dict__,indent=6)
    session_save.close()
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

session_save = open("last_session_info.json","r")
last_session_data = json.load(session_save)
if last_session_data["language"] != None:
    directories = [d for d in manager.os.listdir("languages") if manager.os.path.isdir(manager.os.path.join("languages", d))]
    if last_session_data["language"] not in directories:
        messagebox.showwarning("Error Loading","Could not load language from last session - Missing")
    else:
        manager.get("main").language_name = last_session_data["language"]
        saving.load_groups(last_session_data["language"])
        if last_session_data["letter_editor"] != None:
            letters_path = manager.os.path.join("languages", manager.get("main").language_name, "letters")
            letters = [f for f in manager.os.listdir(letters_path) if manager.os.path.isfile(manager.os.path.join(letters_path, f))]
            if last_session_data["letter_editor"] + ".json" not in letters:
                messagebox.showwarning("Error Loading","Could not load letter from last session - Missing")
            else:
                manager.editor_canvas.load_letter(saving.load_letter(manager.get("main").language_name,last_session_data["letter_editor"],True),last_session_data["letter_editor"])
                manager.editor_canvas.saved = True
        if last_session_data["letter_config"] != None:
            letters_path = manager.os.path.join("languages", manager.get("main").language_name, "letters")
            letters = [f for f in manager.os.listdir(letters_path) if manager.os.path.isfile(manager.os.path.join(letters_path, f))]
            if last_session_data["letter_config"] + ".json" not in letters:
                messagebox.showwarning("Error Loading","Could not load letter from last session - Missing")
            else:
                manager.positioning_canvas.load_letter(saving.load_letter(manager.get("main").language_name,last_session_data["letter_config"],True),last_session_data["letter_config"])
                if saving.does_positioning_for_letter_exist(manager.window.language_name,last_session_data["letter_config"]):
                    manager.positioning_canvas.load_slots(saving.load_positioning(manager.window.language_name,last_session_data["letter_config"],False,True))
                manager.positioning_canvas.saved = True
session_save.close()
manager.get("main").mainloop()