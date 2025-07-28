import os,sys
from tkinter import *
from tkinter import messagebox
from tkinter import simpledialog
from tkinter import colorchooser
from tkinter.ttk import *
import tkinter.font as font
from PIL import Image, ImageTk

import debug_console as debug
import letter_core as letter
import saving_agent as saving
#________GENERAL FUNCTIONS______________
on_windows = sys.platform != "darwin"
registered = {}
group_selector_open = False
language_selector_open = False
letter_selector_open = False
save_window_open = False
focused = 0
def change_tab(name) -> None:
    if name == window.current_frame:
        return
    if name == "EDITOR":
        smart_place(editor_frame,(0,60),(0,60))
        config_frame.place_forget()
        editor_canvas.active = True
        positioning_canvas.active = False
        editor_frame.lift()
        window.current_frame = name
    elif name == "WRITE":
        window.current_frame = name
    elif name == "CONFIG":
        editor_frame.place_forget()
        smart_place(config_frame,(0,60),(0,60))
        editor_canvas.active = False
        positioning_canvas.active = True
        config_frame.lift()
        window.current_frame = name

def smart_place(widget,pos_windows:tuple,pos_mac:tuple):
    if on_windows:
        widget.place(x=pos_windows[0],y=pos_windows[1])
    else:
        widget.place(x=pos_mac[0],y=pos_mac[1])

def get(name) -> Tk:
    if name in registered.keys():
        return registered[name]
    else:
        debug.send("ERROR: Could not find window, defaulting to main")
        return registered["main"]

def register(name,root:Tk):
    global registered
    registered[name] = root

def close(name):
    registered[name].destroy()
    del registered[name]

def visibility(master:Tk,visible:bool):
    if visible:
        master.deiconify()
        master.lift()
    else:
        master.withdraw()

def show_frame(frame:Frame):
    global focused
    focused = frame.id
    frame.tkraise()

#_______BUTTON FUNCTIONS________________
def config_canvas_unload_letter():
    positioning_canvas.letter = None
    positioning_canvas.update()

def save_button_func():
    if window.current_frame == "EDITOR":
        save_letter_editor()
    elif window.current_frame == "CONFIG":
        save_positioning_config()

def on_zoom_slider_change(event):
    config_canvas_zoom_stringvar.set(str(config_canvas_zoom_intvar.get()/100))
    positioning_canvas.zoom = config_canvas_zoom_intvar.get()/100
    positioning_canvas.zoom_changed()

def on_segment_select(event):
    selected_index = editor_segment_listbox.curselection()
    if selected_index:
         editor_canvas.light_reset(False)
         editor_canvas.selected_segment = selected_index[0]
         editor_canvas.update()

def on_segment_double_click(event):
    selected_index = editor_segment_listbox.curselection()
    if selected_index:
        segment = editor_canvas.letter.segments[selected_index[0]]
        new_name = simpledialog.askstring("Rename Segment", "Enter new name:", initialvalue=segment.name)
        if new_name:
            segment.name = new_name
            editor_segment_listbox.delete(selected_index)
            editor_segment_listbox.insert(selected_index, new_name)

def new_segment_button():
    editor_canvas.letter.segments.append(letter.Segment())
    editor_canvas.reload_segments = True

def delete_segment_button():
    selected_index = editor_segment_listbox.curselection()
    if selected_index and len(editor_canvas.letter.segments) > 1:
        editor_segment_listbox.delete(selected_index)
        editor_canvas.letter.segments.pop(selected_index[0])
        editor_canvas.selected_segment = 0
        editor_canvas.light_reset(False)
        editor_canvas.update()

def on_group_double_click(event):
    selected_index = editor_group_listbox.curselection()
    if selected_index:
        group = editor_canvas.letter.groups[selected_index[0]]
        new_name = simpledialog.askstring("Rename Group", "Enter new name:", initialvalue=group)
        if new_name:
            new_name = new_name.upper()
            editor_canvas.saved = False
            editor_canvas.letter.groups.pop(selected_index[0])
            editor_canvas.letter.groups.insert(selected_index[0],new_name)
            saving.rename_group(get("main").language_name,group,new_name)
            editor_group_listbox.delete(selected_index)
            editor_group_listbox.insert(selected_index, new_name)

def delete_group_button():
    selected_index = editor_group_listbox.curselection()
    if selected_index:
        editor_group_listbox.delete(selected_index)
        editor_canvas.letter.groups.pop(selected_index[0])

def delete_letter_space():
    positioning_canvas.keys_pressed.append("backspace")

def delete_connector_or_node():
    editor_canvas.keys_pressed.append("backspace")
    editor_canvas.process_key_presses(True)

def turn_selected_connectors_into_lines():
    editor_canvas.keys_pressed.append("l")
    editor_canvas.process_key_presses(True)

def turn_selected_connectors_into_beziers():
    editor_canvas.keys_pressed.append("b")
    editor_canvas.process_key_presses(True)

def turn_selected_connectors_into_half_circles():
    editor_canvas.keys_pressed.append("c")
    editor_canvas.process_key_presses(True)
def rotate_left():
    rotation = rotation_var.get()
    try:
        rotation = float(rotation)
    except ValueError:
        rotation = 0.0
    editor_canvas.rotate_selection(-rotation)

def rotate_right():
    rotation = rotation_var.get()
    try:
        rotation = float(rotation)
    except ValueError:
        rotation = 0.0
    editor_canvas.rotate_selection(rotation)

def mirror_y():
    editor_canvas.mirror_selection()

def mirror_x():
    editor_canvas.mirror_selection(True,False)

def on_toggle_draw_nodes():
    editor_canvas.draw_nodes = show_nodes_var.get()
    editor_canvas.update()

def validate_angle(new_value):
    if new_value == "":
        return True
    try:
        val = float(new_value)
        return 0 <= val <= 360
    except ValueError:
        return False

def validate_is_number(new_value):
    if new_value == "" or new_value == "-":
        return True
    try:
        val = float(new_value)
        return True
    except ValueError:
        return False

def on_center_change_x(new_value):
    try:
        center_x = float(new_value if new_value != "" else "0")
        center_y = float(center_y_var.get() if center_y_var.get() != "" else "0")
        if editor_canvas.center_edits.x != center_x or editor_canvas.center_edits.y != center_y:
            editor_canvas.center_edits.x = center_x
            editor_canvas.center_edits.y = center_y
            editor_canvas.update()
    except ValueError:
        pass
    return True

def on_center_change_y(new_value):
    try:
        center_x = float(center_x_var.get() if center_x_var.get() != "" else "0")
        center_y = float(new_value if new_value != "" else "0")
        if editor_canvas.center_edits.x != center_x or editor_canvas.center_edits.y != center_y:
            editor_canvas.center_edits.x = center_x
            editor_canvas.center_edits.y = center_y
            editor_canvas.update()
    except ValueError:
        pass
    return True

def open_group_selector():
    #Base written by Copilot
    global group_selector_open
    if not ((editor_canvas.saved and window.current_frame == "EDITOR") or (positioning_canvas.saved and window.current_frame == "CONFIG")):
        return
    def on_ok():
        selected_index = listbox.curselection()
        if selected_index:
            editor_canvas.saved = False
            for index in selected_index:
                selected_group = listbox.get(index)
                if selected_group not in editor_canvas.letter.groups:
                        editor_canvas.letter.groups.append(selected_group)
                        editor_group_listbox.insert(END,selected_group)
        else:
            messagebox.showwarning("No selection", "Please select at least one group.")
    def on_cancel():
        close_group_selector()
    def on_new():
        def on_submit():
            new_group_name = name_entry.get()
            new_group_color = color_var.get()
            selected_parent_index = parent_combobox.current()
            if selected_parent_index >= 0:
                new_group_parent = saving.all_groups[selected_parent_index].name
            else:
                new_group_parent = "None"

            if new_group_name:
                debug.send(f"NEW GROUP: Name={new_group_name}, Color={new_group_color}, Parent={new_group_parent}")
                saving.create_group(window.language_name,letter.Group(new_group_name,new_group_color,new_group_parent))
                listbox.insert(END,new_group_name)
                close_new_group_dialog()

        def close_new_group_dialog():
            new_group_dialog.destroy()

        def choose_color():
            color_code = colorchooser.askcolor(title="Choose color")[1]
            if color_code:
                color_var.set(color_code)

        new_group_dialog = Toplevel(window)
        new_group_dialog.title("New Group")
        new_group_dialog.geometry("300x400")
        new_group_dialog.protocol("WM_DELETE_WINDOW", close_new_group_dialog)

        name_label = Label(new_group_dialog, text="Name:")
        name_label.pack(pady=5)
        name_entry = Entry(new_group_dialog)
        name_entry.pack(pady=5)

        color_label = Label(new_group_dialog, text="Color:")
        color_label.pack(pady=5)
        color_var = StringVar()
        color_button = Button(new_group_dialog, text="Choose Color", command=choose_color)
        color_button.pack(pady=5)
        color_entry = Entry(new_group_dialog, textvariable=color_var)
        color_entry.pack(pady=5)

        parent_label = Label(new_group_dialog, text="Parent Group:")
        parent_label.pack(pady=5)
        parent_combobox = Combobox(new_group_dialog, values=[group.name for group in saving.all_groups])
        parent_combobox.pack(pady=5)

        submit_button = Button(new_group_dialog, text="Submit", command=on_submit)
        submit_button.pack(pady=10)

        cancel_button = Button(new_group_dialog, text="Cancel", command=close_new_group_dialog)
        cancel_button.pack(pady=5)
    def close_group_selector():
        global group_selector_open
        close("group_selector")
        group_selector_open = False
    def on_group_double_click(event):
        selected_index = listbox.curselection()
        if selected_index:
            group = saving.all_groups[selected_index[0]]
            new_name = simpledialog.askstring("Rename Group", "Enter new name:", initialvalue=group.name)
            if new_name:
                new_name = new_name.upper()
                editor_canvas.saved = False
                if group.name in editor_canvas.letter.groups:
                    editor_canvas.letter.groups.pop(selected_index[0])
                    editor_canvas.letter.groups.insert(selected_index[0],new_name)
                    editor_group_listbox.delete(selected_index)
                    editor_group_listbox.insert(selected_index, new_name)
                saving.rename_group(get("main").language_name,group.name,new_name)
                listbox.delete(selected_index)
                listbox.insert(selected_index, new_name)
    group_selector_open = True
    group_selector = Toplevel(window)
    register("group_selector",group_selector)
    group_selector.title("Select Group(s)")
    group_selector.geometry("300x400")
    group_selector.protocol("WM_DELETE_WINDOW", close_group_selector)

    listbox = Listbox(group_selector)
    listbox.pack(fill=BOTH, expand=True, padx=10, pady=10)
    listbox.bind('<Double-1>', on_group_double_click)

    for group in saving.all_groups:
        listbox.insert(END, group.name)

    button_frame = Frame(group_selector)
    button_frame.pack(fill=X, padx=10, pady=10)

    ok_button = Button(button_frame, text="OK", command=on_ok)
    ok_button.pack(side=LEFT, padx=5)

    cancel_button = Button(button_frame, text="Cancel", command=on_cancel)
    cancel_button.pack(side=LEFT, padx=5)

    new_button = Button(button_frame, text="New", command=on_new)
    new_button.pack(side=LEFT, padx=5)

def open_language_selector():
    #Base written by Copilot
    if not ((editor_canvas.saved and window.current_frame == "EDITOR") or (positioning_canvas.saved and window.current_frame == "CONFIG")):
        ask_save("language")
        return
    global language_selector_open
    if language_selector_open:
        return
    def on_ok():
        selected_index = listbox.curselection()
        if selected_index:
            selected_language = listbox.get(selected_index)
            window.language_name = selected_language
            saving.load_groups(selected_language)
            create_new_letter()
            close_language_selector()
        else:
            messagebox.showwarning("No selection", "Please select a language.")
    def on_cancel():
        close_language_selector()
    def on_new():
        new_language_name = simpledialog.askstring("New Language", "Enter the name of the new language:")
        if new_language_name:
            new_language_path = os.path.join(path, new_language_name)
            letters_path = os.path.join(new_language_path, "letters")
            os.makedirs(letters_path)
            listbox.insert(END, new_language_name)
            window.language_name = new_language_name
            saving.all_groups = []
            saving.create_config_file(new_language_name)
            create_new_letter()
            close_language_selector()
    def close_language_selector():
        global language_selector_open
        close("language_selector")
        language_selector_open = False
    def on_language_double_click(event):
        selected_index = listbox.curselection()
        if selected_index:
            language = listbox.get(selected_index)
            new_name = simpledialog.askstring("Rename Language", "Enter new name:", initialvalue=language)
            if new_name and new_name != language:
                os.rename(os.path.join(path, language),os.path.join(path, new_name))
                listbox.delete(selected_index)
                listbox.insert(selected_index, new_name)
    language_selector_open = True
    language_selector = Toplevel(window)
    register("language_selector",language_selector)
    language_selector.title("Select Language")
    language_selector.geometry("300x400")
    language_selector.protocol("WM_DELETE_WINDOW", close_language_selector)

    listbox = Listbox(language_selector)
    listbox.pack(fill=BOTH, expand=True, padx=10, pady=10)
    listbox.bind('<Double-1>', on_language_double_click)

    path = "languages"
    directories = [d for d in os.listdir(path) if os.path.isdir(os.path.join(path, d))]
    for directory in directories:
        listbox.insert(END, directory)

    button_frame = Frame(language_selector)
    button_frame.pack(fill=X, padx=10, pady=10)

    ok_button = Button(button_frame, text="OK", command=on_ok)
    ok_button.pack(side=LEFT, padx=5)

    cancel_button = Button(button_frame, text="Cancel", command=on_cancel)
    cancel_button.pack(side=LEFT, padx=5)

    new_button = Button(button_frame, text="New", command=on_new)
    new_button.pack(side=LEFT, padx=5)

def open_letter_selector():
    if not ((editor_canvas.saved and window.current_frame == "EDITOR") or (positioning_canvas.saved and window.current_frame == "CONFIG")):
        ask_save("open")
        return
    if window.language_name == "":
        messagebox.showwarning("No selection", "Please select a language.")
        return
    global letter_selector_open

    language = window.language_name

    if letter_selector_open:
        return

    def on_open():
        selected_item = tree.selection()
        if selected_item:
            selected_letter = tree.item(selected_item, "text")
            if window.current_frame == "EDITOR":
                editor_canvas.load_letter(saving.load_letter(window.language_name, selected_letter, True), selected_letter)
                editor_canvas.saved = True
            elif window.current_frame == "CONFIG":
                positioning_canvas.load_letter(saving.load_letter(window.language_name, selected_letter, True), selected_letter,not keep_slots_boolvar.get())
                if saving.does_positioning_for_letter_exist(window.language_name,selected_letter) and not keep_slots_boolvar.get():
                    positioning_canvas.load_slots(saving.load_positioning(window.language_name,selected_letter,False,True))
                positioning_canvas.saved = True
            close_letter_selector()
        else:
            messagebox.showwarning("No selection", "Please select a letter.")

    def on_close():
        close_letter_selector()

    def close_letter_selector():
        global letter_selector_open
        close("letter_selector")
        letter_selector_open = False
    
    def on_letter_select(event):
        selected_item = tree.selection()
        if selected_item:
            selected_letter = tree.item(selected_item, "text")
            # Load and display the preview image in the label
            preview_path = os.path.join("languages", window.language_name, "previews", f"{selected_letter}.png")
            if os.path.exists(preview_path):
                img = Image.open(preview_path)
                w, h = img.size
                # Calculate cropping box for a centered square
                if w > h:
                    left = (w - h) // 2
                    right = left + h
                    img = img.crop((left, 0, right, h))
                img = img.resize((150, 150), Image.LANCZOS)
                photo = ImageTk.PhotoImage(img, master=preview_label)
                preview_label.config(image=photo)
                preview_label.image = photo  # Prevent garbage collection
            else:
                preview_label.config(image="", text="No preview available")
                preview_label.image = None

    def on_letter_double_click(event):
        selected_item = tree.selection()
        if selected_item:
            letter_name = tree.item(selected_item, "text")
            new_name = simpledialog.askstring("Rename Letter", "Enter new name:", initialvalue=letter_name)
            if new_name and new_name != letter_name:
                os.rename(os.path.join(letters_path, letter_name + ".json"), os.path.join(letters_path, new_name + ".json"))
                tree.item(selected_item, text=new_name)

    def on_group_filter_change(event):
        selected_group = group_filter_combobox.get()
        if selected_group != "All":
            style.configure("Custom.TCombobox", fieldbackground=saving.get_group_obj(selected_group).color)
        tree.delete(*tree.get_children())
        for letter_name, letter_groups in groups.items():
            if selected_group == "All" or selected_group in letter_groups:
                if letter_groups:
                    tree.insert("", "end", text=letter_name, tags=letter_groups[0])
                else:
                    tree.insert("", "end", text=letter_name)

    style.configure("Custom.TCombobox", fieldbackground="white")
    letter_selector_open = True
    letter_selector = Toplevel(window)
    register("letter_selector", letter_selector)
    letter_selector.title("Select Letter")
    letter_selector.geometry("300x500")
    letter_selector.protocol("WM_DELETE_WINDOW", close_letter_selector)

    # Use a Label for the preview image
    preview_label = Label(letter_selector, width=150, anchor="center", text="No preview")
    preview_label.pack(pady=10)

    tree = Treeview(letter_selector, show="tree")
    tree.pack(fill=BOTH, expand=True, padx=10, pady=10)
    tree.bind("<<TreeviewSelect>>", on_letter_select)
    tree.bind("<Double-1>", on_letter_double_click)

    letters_path = os.path.join("languages", language, "letters")
    letters = [f for f in os.listdir(letters_path) if os.path.isfile(os.path.join(letters_path, f))]

    groups = {}
    for let in letters:
        let = os.path.splitext(let)[0]
        groups[let] = saving.get_group_of_letter(window.language_name, let)
        if groups[let]:
            tree.insert("", "end", text=let, tags=groups[let][0])
        else:
            tree.insert("", "end", text=let)

    group_filter_frame = Frame(letter_selector)
    group_filter_frame.pack(fill=X, padx=10, pady=5)

    group_filter_label = Label(group_filter_frame, text="Filter by Group:")
    group_filter_label.pack(side=LEFT, padx=5)

    all_groups = {"All"}
    for letter_groups in groups.values():
        all_groups.update(letter_groups)

    for group in all_groups:
        if group == "All":
            continue
        tree.tag_configure(group, background=saving.get_group_obj(group).color)

    group_filter_combobox = Combobox(group_filter_frame, values=list(all_groups), state="readonly", style="Custom.TCombobox")
    group_filter_combobox.set("All")
    group_filter_combobox.pack(fill=X, expand=True, padx=5)
    group_filter_combobox.bind("<<ComboboxSelected>>", on_group_filter_change)

    button_frame = Frame(letter_selector)
    button_frame.pack(fill=X, padx=10, pady=10)

    open_button = Button(button_frame, text="Open", command=on_open)
    open_button.pack(side=LEFT, padx=5)

    close_button = Button(button_frame, text="Close", command=on_close)
    close_button.pack(side=LEFT, padx=5)

    if window.current_frame == "CONFIG":
        keep_slots_boolvar = BooleanVar(letter_selector)
        keep_slots = Checkbutton(button_frame,text="Keep Slots",state=OFF,variable=keep_slots_boolvar)
        keep_slots.pack(side=LEFT, padx=5)

def open_positioning_window(use_editor_version:bool = True):
    if not ((editor_canvas.saved and window.current_frame == "EDITOR") or (positioning_canvas.saved and window.current_frame == "CONFIG")):
        ask_save("open")
        return
    if window.language_name == "":
        messagebox.showwarning("No selection", "Please select a language.")
        return
    global letter_selector_open

    language = window.language_name

    if letter_selector_open:
        return

    def on_open():
        selected_index = listbox.curselection()
        if selected_index:
            selected_letter = listbox.get(selected_index)
            positioning_canvas.load_slots(saving.load_positioning(window.language_name,selected_letter,positioning_selector.open_tab == "TEMPLATE",use_editor_version))
            positioning_canvas.saved = True
            close_letter_selector()
        else:
            messagebox.showwarning("No selection", "Please select a letter.")

    def on_close():
        close_letter_selector()

    def close_letter_selector():
        global letter_selector_open
        close("pos_selector")
        letter_selector_open = False

    def on_letter_double_click(event):
        selected_index = listbox.curselection()
        if selected_index:
            letter_name = listbox.get(selected_index)
            new_name = simpledialog.askstring("Rename Positioning/Template", "Enter new name:", initialvalue=letter_name)
            letters_path = os.path.join("languages", language, "positioning","templates" if positioning_canvas.letter is None else "letters")
            if new_name and new_name != letter_name:
                os.rename(os.path.join(letters_path, letter_name + ".json"), os.path.join(letters_path, new_name + ".json"))
                listbox.delete(selected_index)
                listbox.insert(selected_index,new_name)
    
    def change_tab(new_tab:str):
        if new_tab == "TEMPLATE" and positioning_selector.open_tab != "TEMPLATE":
            positioning_selector.title("Select Template")
            positioning_selector.open_tab = "TEMPLATE"

            letters_path = os.path.join("languages", language, "positioning","templates")
            letters = [f for f in os.listdir(letters_path) if os.path.isfile(os.path.join(letters_path, f))]
            listbox.delete(0,END)
            for let in letters:
                listbox.insert(END, os.path.splitext(let)[0])
        elif new_tab == "LETTER" and positioning_selector.open_tab != "LETTER":
            positioning_selector.title("Select Letter Positioning")
            positioning_selector.open_tab = "LETTER"

            letters_path = os.path.join("languages", language, "positioning","letters")
            letters = [f for f in os.listdir(letters_path) if os.path.isfile(os.path.join(letters_path, f))]
            listbox.delete(0,END)
            for let in letters:
                listbox.insert(END, os.path.splitext(let)[0])

    style.configure("Custom.TCombobox", fieldbackground="white")
    letter_selector_open = True
    positioning_selector = Toplevel(window)
    register("pos_selector", positioning_selector)
    positioning_selector.geometry("300x500")
    positioning_selector.protocol("WM_DELETE_WINDOW", close_letter_selector)

    letters_button = Button(positioning_selector,text="Letters",command=lambda:change_tab("LETTER"))
    letters_button.pack(padx=10, pady=10)

    template_button = Button(positioning_selector,text="Templates",command=lambda:change_tab("TEMPLATE"))
    template_button.pack(padx=10, pady=10)

    listbox = Listbox(positioning_selector)
    listbox.pack(fill=BOTH, expand=True, padx=10, pady=10)
    listbox.bind("<Double-1>", on_letter_double_click)

    if positioning_canvas.letter is None:
        positioning_selector.title("Select Template")
        letters_path = os.path.join("languages", language, "positioning","templates")
        positioning_selector.open_tab = "TEMPLATE"
    else:
        positioning_selector.title("Select Letter Positioning")
        letters_path = os.path.join("languages", language, "positioning","letters")
        positioning_selector.open_tab = "LETTER"

    letters = [f for f in os.listdir(letters_path) if os.path.isfile(os.path.join(letters_path, f))]

    for let in letters:
        listbox.insert(END, os.path.splitext(let)[0])

    button_frame = Frame(positioning_selector)
    button_frame.pack(fill=X, padx=10, pady=10)

    open_button = Button(button_frame, text="Open", command=on_open)
    open_button.pack(side=LEFT, padx=5)

    close_button = Button(button_frame, text="Close", command=on_close)
    close_button.pack(side=LEFT, padx=5)

def save_letter_editor():
    global letter_selector_open

    language = window.language_name

    if letter_selector_open:
        return

    def on_save():
        selected_index = listbox.curselection()
        if selected_index:
            selected_letter = listbox.get(selected_index)
            debug.send(f"Saving {selected_letter}[{window.language_name}]")
            saving.save_letter(window.language_name,selected_letter,editor_canvas.letter)
            editor_canvas.letter_name = selected_letter
            editor_canvas.saved = True
            close_letter_selector()
        else:
            entered_name = entry.get()
            if entered_name:
                debug.send(f"Saving {entered_name}[{window.language_name}]")
                saving.save_letter(window.language_name,entered_name,editor_canvas.letter)
                editor_canvas.letter_name = entered_name
                editor_canvas.saved = True
                close_letter_selector()
            else:
                messagebox.showwarning("No name", "Please enter a name or select a letter.")
    
    def on_cancel():
        close_letter_selector()

    def close_letter_selector():
        global letter_selector_open
        close("save_letter_editor")
        letter_selector_open = False

    def on_letter_select(event):
        selected_index = listbox.curselection()
        if selected_index:
            selected_letter = listbox.get(selected_index)
            entry.delete(0, END)
            entry.insert(0, selected_letter)

    letter_selector_open = True
    save_window = Toplevel(window)
    register("save_letter_editor",save_window)
    save_window.title("Save Letter")
    save_window.geometry("300x400")
    save_window.protocol("WM_DELETE_WINDOW", close_letter_selector)

    listbox = Listbox(save_window)
    listbox.pack(fill=BOTH, expand=True, padx=10, pady=10)
    listbox.bind('<<ListboxSelect>>', on_letter_select)

    letters_path = os.path.join("languages", language, "letters")
    letters = [f for f in os.listdir(letters_path) if os.path.isfile(os.path.join(letters_path, f))]
    for let in letters:
        listbox.insert(END, os.path.splitext(let)[0])

    entry_frame = Frame(save_window)
    entry_frame.pack(fill=X, padx=10, pady=10)

    entry_label = Label(entry_frame, text="Enter name:")
    entry_label.pack(side=LEFT, padx=5)

    txt_var = StringVar(entry_frame,editor_canvas.letter_name)
    entry = Entry(entry_frame,textvariable=txt_var)
    entry.txt_var = txt_var
    entry.pack(fill=X, expand=True, padx=5)

    button_frame = Frame(save_window)
    button_frame.pack(fill=X, padx=10, pady=10)

    save_button = Button(button_frame, text="Save", command=on_save)
    save_button.pack(side=LEFT, padx=5)

    cancel_button = Button(button_frame, text="Cancel", command=on_cancel)
    cancel_button.pack(side=LEFT, padx=5)

def save_positioning_config():
    global letter_selector_open

    language = window.language_name

    if letter_selector_open:
        return

    def on_save():
        selected_index = listbox.curselection()
        if selected_index:
            selected_letter = listbox.get(selected_index)
            debug.send(f"Saving {selected_letter}[{window.language_name}]")
            saving.save_positioning(window.language_name,selected_letter,positioning_canvas.slots,save_window.open_tab == "TEMPLATE")
            positioning_canvas.letter_name = selected_letter
            positioning_canvas.saved = True
            close_letter_selector()
        else:
            entered_name = entry.get()
            if entered_name:
                debug.send(f"Saving {entered_name}[{window.language_name}]")
                saving.save_positioning(window.language_name,selected_letter,positioning_canvas.slots,save_window.open_tab == "TEMPLATE")
                positioning_canvas.letter_name = entered_name
                positioning_canvas.saved = True
                close_letter_selector()
            else:
                messagebox.showwarning("No name", "Please enter a name or select a letter.")
    
    def on_cancel():
        close_letter_selector()

    def close_letter_selector():
        global letter_selector_open
        close("save_positioning_config")
        letter_selector_open = False

    def on_letter_select(event):
        selected_index = listbox.curselection()
        if selected_index:
            selected_letter = listbox.get(selected_index)
            entry.delete(0, END)
            entry.insert(0, selected_letter)
    
    def change_tab(new_tab:str):
        if new_tab == "TEMPLATE" and save_window.open_tab != "TEMPLATE":
            save_window.title("Save Template")
            save_window.open_tab = "TEMPLATE"

            letters_path = os.path.join("languages", language, "positioning","templates")
            letters = [f for f in os.listdir(letters_path) if os.path.isfile(os.path.join(letters_path, f))]
            listbox.delete(0,END)
            for let in letters:
                listbox.insert(END, os.path.splitext(let)[0])
        elif new_tab == "LETTER" and save_window.open_tab != "LETTER":
            save_window.title("Save Letter Positioning")
            save_window.open_tab = "LETTER"

            letters_path = os.path.join("languages", language, "letters")
            letters = [f for f in os.listdir(letters_path) if os.path.isfile(os.path.join(letters_path, f))]
            listbox.delete(0,END)
            for let in letters:
                listbox.insert(END, os.path.splitext(let)[0])

    letter_selector_open = True
    save_window = Toplevel(window)
    register("save_positioning_config",save_window)
    save_window.geometry("300x400")
    save_window.protocol("WM_DELETE_WINDOW", close_letter_selector)

    letters_button = Button(save_window,text="Letters",command=lambda:change_tab("LETTER"))
    letters_button.pack(padx=10, pady=10)

    template_button = Button(save_window,text="Templates",command=lambda:change_tab("TEMPLATE"))
    template_button.pack(padx=10, pady=10)

    listbox = Listbox(save_window)
    listbox.pack(fill=BOTH, expand=True, padx=10, pady=10)
    listbox.bind('<<ListboxSelect>>', on_letter_select)

    #Default to template or letter depending on what is currently present in editor
    if positioning_canvas.letter is None:
        save_window.title("Save Template")
        letters_path = os.path.join("languages", language, "positioning","templates")
        save_window.open_tab = "TEMPLATE"
    else:
        save_window.title("Save Letter Positioning")
        letters_path = os.path.join("languages", language, "letters")
        save_window.open_tab = "LETTER"
    letters = [f for f in os.listdir(letters_path) if os.path.isfile(os.path.join(letters_path, f))]
    for let in letters:
        listbox.insert(END, os.path.splitext(let)[0])

    entry_frame = Frame(save_window)
    entry_frame.pack(fill=X, padx=10, pady=10)

    entry_label = Label(entry_frame, text="Enter name:")
    entry_label.pack(side=LEFT, padx=5)

    txt_var = StringVar(entry_frame,positioning_canvas.letter_name)
    entry = Entry(entry_frame,textvariable=txt_var)
    entry.txt_var = txt_var
    entry.pack(fill=X, expand=True, padx=5)

    button_frame = Frame(save_window)
    button_frame.pack(fill=X, padx=10, pady=10)

    save_button = Button(button_frame, text="Save", command=on_save)
    save_button.pack(side=LEFT, padx=5)

    cancel_button = Button(button_frame, text="Cancel", command=on_cancel)
    cancel_button.pack(side=LEFT, padx=5)

def ask_save(action="new"):
    global save_window_open

    if save_window_open:
        return
    def on_save():
        save_button_func()
        close_save_window()

    def on_ignore():
        #actions: new, language, open
        editor_canvas.saved = True
        if action == "new":
            create_new_letter()
        if action == "language":
            open_language_selector()
        if action == "open":
            open_letter_selector()
        close_save_window()

    def on_cancel():
        close_save_window()
    
    def close_save_window():
        global save_window_open
        close("save_window")
        save_window_open = False

    save_window_open = True
    save_window = Toplevel(window)
    register("save_window",save_window)
    save_window.title("Save Changes")
    save_window.geometry("300x150")
    save_window.protocol("WM_DELETE_WINDOW", close_save_window)

    label = Label(save_window, text="Are you sure you don't want to save?")
    label.pack(pady=20)

    button_frame = Frame(save_window)
    button_frame.pack(pady=10)

    save_button = Button(button_frame, text="Save", command=on_save)
    save_button.pack(side=LEFT, padx=5)

    ignore_button = Button(button_frame, text="Ignore", command=on_ignore)
    ignore_button.pack(side=LEFT, padx=5)

    cancel_button = Button(button_frame, text="Cancel", command=on_cancel)
    cancel_button.pack(side=LEFT, padx=5)

def create_new_letter():
    if not ((editor_canvas.saved and window.current_frame == "EDITOR") or (positioning_canvas.saved and window.current_frame == "CONFIG")):
        ask_save("new")
        return
    if window.current_frame == "EDITOR":
        editor_canvas.saved = True
        new_letter = letter.Letter()
        new_letter.segments.append(letter.Segment())
        editor_canvas.load_letter(new_letter,"Unnamed")
    elif window.current_frame == "CONFIG":
        positioning_canvas.saved = True
        positioning_canvas.load_letter(None,"Unnamed")

def process_inspector_menu(event):
    #Check if anything was changed
    change = False
    for i,entry_x,var_x,entry_y,var_y in zip(range(4),inspector_entries_x,inspector_vars_x,inspector_entries_y,inspector_vars_y):
        if i >= window.shown_inspector_entries:
            break
        if entry_x.original_value != var_x.get():
            change = True
            break
        if entry_y.original_value != var_y.get():
            change = True
            break
    if not change:
        debug.send("Nothing changed!")
        return
    else:
        if editor_canvas.selection_type == "node":
            #This should work for simple selections and multiple ones
            dx = float(inspector_entries_x[0].get()) - float(inspector_entries_x[0].original_value)
            dy = float(inspector_entries_y[0].get()) - float(inspector_entries_y[0].original_value)
            inspector_entries_x[0].original_value = inspector_entries_x[0].get()
            inspector_entries_y[0].original_value = inspector_entries_y[0].get()
            for node in editor_canvas.letter.segments[editor_canvas.selected_segment].nodes:
                if node.selected:
                    node.x += dx
                    node.y += dy
        elif editor_canvas.selection_type == "connector":
            for i,connector in enumerate(editor_canvas.letter.segments[editor_canvas.selected_segment].connectors):
                if connector.selected:
                    node1 = editor_canvas.letter.segments[editor_canvas.selected_segment].nodes[i]
                    node2 = editor_canvas.letter.segments[editor_canvas.selected_segment].nodes[(i+1)%len(editor_canvas.letter.segments[editor_canvas.selected_segment].connectors)]
                    node1.x = float(inspector_entries_x[0].get())
                    node1.y = float(inspector_entries_y[0].get())
                    node2.x = float(inspector_entries_x[1].get())
                    node2.y = float(inspector_entries_y[1].get())
                    inspector_entries_x[0].original_value = inspector_entries_x[0].get()
                    inspector_entries_y[0].original_value = inspector_entries_y[0].get()
                    inspector_entries_x[1].original_value = inspector_entries_x[1].get()
                    inspector_entries_y[1].original_value = inspector_entries_y[1].get()
                    if connector.type == "BEZIER":
                        connector.anchors[0].x = float(inspector_entries_x[2].get())
                        connector.anchors[0].y = float(inspector_entries_y[2].get())
                        connector.anchors[1].x = float(inspector_entries_x[3].get())
                        connector.anchors[1].y = float(inspector_entries_y[3].get())
                        inspector_entries_x[2].original_value = inspector_entries_x[2].get()
                        inspector_entries_y[2].original_value = inspector_entries_y[2].get()
                        inspector_entries_x[3].original_value = inspector_entries_x[3].get()
                        inspector_entries_y[3].original_value = inspector_entries_y[3].get()
                    if connector.type == "CIRCLE":
                        if abs(float(inspector_entries_x[2].get())) == float(inspector_entries_x[2].get()):
                            connector.direction = 1
                        else:
                            connector.direction = -1
                    break
        editor_canvas.saved = False
        editor_canvas.update()

def process_config_inspector_menu(event):
    #Check if anything was changed
    change = False
    changed_index = -1
    for i,entry_x,var_x,entry_y,var_y in zip(range(2),config_inspector_entries_x,config_inspector_vars_x,config_inspector_entries_y,config_inspector_vars_y):
        if i >= window.shown_inspector_entries:
            break
        if entry_x.original_value != var_x.get():
            changed_index = i
            change = True
            break
        if entry_y.original_value != var_y.get():
            changed_index = i
            change = True
            break
    if not change:
        debug.send("Nothing changed!")
        return
    else:
        #This should work for simple selections and multiple ones
        dx = float(config_inspector_entries_x[i].get()) - float(config_inspector_entries_x[i].original_value)
        dy = float(config_inspector_entries_y[i].get()) - float(config_inspector_entries_y[i].original_value)
        config_inspector_entries_x[i].original_value = config_inspector_entries_x[i].get()
        config_inspector_entries_y[i].original_value = config_inspector_entries_y[i].get()
        for slot in positioning_canvas.slots:
            if slot.selected:
                if changed_index == 0:
                    slot.x += dx
                    slot.y += dy
                else:
                    slot.width += dx
                    slot.height += dy
        positioning_canvas.saved = False
        positioning_canvas.update()

window = Tk()
window.language_name = ""
window.current_frame = "EDITOR" #EDITOR, WRITE, CONFIG
#Tk Variables
editor_txt_selected_label = StringVar(window)
editor_txt_selected_label.set("Selected: Placeholder [Placeholder]")
config_txt_selected_label = StringVar(window)
config_txt_selected_label.set("Selected: Placeholder [Placeholder]")

config_canvas_zoom_stringvar = StringVar(window)
config_canvas_zoom_stringvar.set("1.0")
config_canvas_zoom_intvar = IntVar(window)
#Style
style = Style(window)
style.configure("secondary.TFrame", background="#1a1919")
style.configure("toolbar.TFrame", background="#4a4949")
style.configure("header.TFrame", background="#9e9d9d")
style.configure("highlight.TListbox", background="#bfbfbf")
style.configure("Custom.TCombobox", fieldbackground="lightblue", background="white")

window.geometry("1000x800")
background = Frame(window,width=1000,height=800,style="secondary.TFrame")
background.pack()
background.lift()

window.lift()
window.title("Scriptor - Letter Editor")

toolbar_frame = Frame(window,height=40,width=600,style="toolbar.TFrame")
new_button = Button(toolbar_frame, text="New",width=10 if on_windows else 7,command=lambda: create_new_letter())
save_button = Button(toolbar_frame, text="Save",width=10 if on_windows else 7,command=save_button_func)
open_button = Button(toolbar_frame, text="Open",width=10 if on_windows else 7,command=open_letter_selector)
settings_button = Button(toolbar_frame, text="Settings",width=10 if on_windows else 7,command=lambda: print("SETTINGS"))
language_button = Button(toolbar_frame, text="Language",width=10 if on_windows else 7,command=open_language_selector)
smart_place(new_button,(20,7),(20,7))
smart_place(save_button,(100,7),(130,7))
smart_place(open_button,(180,7),(240,7))
smart_place(settings_button,(260,7),(350,7))
smart_place(language_button,(340,7),(460,7))
smart_place(toolbar_frame,(20,0),(20,0))

navigation_frame = Frame(window,height=50,width=300,style="toolbar.TFrame")
edit_button = Button(navigation_frame, text="Edit",width=10 if on_windows else 7,command=lambda: change_tab("EDITOR"))
configure_button = Button(navigation_frame, text="Configure",width=10 if on_windows else 7,command=lambda: change_tab("CONFIG"))
write_button = Button(navigation_frame, text="Write",width=10 if on_windows else 7,command=lambda: change_tab("WRITE"))
smart_place(write_button,(20,7),(20,7))
smart_place(edit_button,(120,7),(120,7))
smart_place(configure_button,(220,7),(220,7))
smart_place(navigation_frame,(700,0),(700,0))

#__________________________________EDITOR____________________________________________
editor_frame = Frame(window,height=700,width=1000,style="secondary.TFrame")

editor_header_frame = Frame(editor_frame,height=40,width=704,style="header.TFrame")
editor_selected_label = Label(editor_header_frame,font=('Helvetica',15),background="#9e9d9d",textvariable=editor_txt_selected_label)
editor_selected_label.letter = ""
editor_selected_label.language = ""
editor_selected_label.saved = None
smart_place(editor_selected_label,(5,7),(5,7))
smart_place(editor_frame,(0,60),(0,60))
smart_place(editor_header_frame,(5,0),(5,0))

editor_canvas = letter.EditorCanvas(Canvas(editor_frame,width=700,height=600,background="#525252"))
smart_place(editor_canvas.canvas,(5,45),(5,45))

editor_segment_listbox_frame = Frame(editor_frame,width=282,height=300,style="header.TFrame")
smart_place(editor_segment_listbox_frame,(715,349),(715,349))

editor_segment_listbox = Listbox(editor_segment_listbox_frame,width=43,height=15,bg=style.lookup("header.TFrame","background"),highlightcolor=style.lookup("hightlight.TListbox","background"))
editor_segment_listbox.bind('<<ListboxSelect>>', on_segment_select)
editor_segment_listbox.bind('<Double-1>', on_segment_double_click)
smart_place(editor_segment_listbox,(10,45),(10,45))

plus_img = Image.open("images/plus.png")
plus_img = plus_img.resize((20,20))
plus_photo = ImageTk.PhotoImage(plus_img,master=editor_segment_listbox_frame)
editor_new_segment_button = Button(editor_segment_listbox_frame,image=plus_photo,command=new_segment_button)
editor_new_segment_button.plus_photo = plus_photo
smart_place(editor_new_segment_button,(10,10),(10,10))

trash_img = Image.open("images/trash.png")
trash_img = trash_img.resize((20,20))
trash_photo = ImageTk.PhotoImage(trash_img,master=editor_segment_listbox_frame)
editor_delete_segment_button = Button(editor_segment_listbox_frame,image=trash_photo,command=delete_segment_button) 
editor_delete_segment_button.trash_photo = trash_photo
smart_place(editor_delete_segment_button,(60,10),(70,10))

grid_img = Image.open("images/grid.png")
grid_photo = ImageTk.PhotoImage(grid_img,master=window)
editor_canvas.canvas.create_image(0,0,image=grid_photo,anchor="nw",tags=["grid","base"])
editor_canvas.canvas.create_line(350-200,300-200,350+200,300-200,fill="gray",tags="grid")
editor_canvas.canvas.create_line(350-200,300+200,350+200,300+200,fill="gray",tags="grid")
editor_canvas.canvas.create_line(350-200,300-200,350-200,300+200,fill="gray",tags="grid")
editor_canvas.canvas.create_line(350+200,300-200,350+200,300+200,fill="gray",tags="grid")
editor_canvas.grid_photo = grid_photo

inspector_frame = Frame(editor_frame, width=282, height=300, style="header.TFrame")
smart_place(inspector_frame,(715,45),(715,45))

inspector_labels_x = [
    Label(inspector_frame, text=f"X1:", background=style.lookup("header.TFrame", "background")),
    Label(inspector_frame, text=f"X2:", background=style.lookup("header.TFrame", "background")),
    Label(inspector_frame, text=f"X3:", background=style.lookup("header.TFrame", "background")),
    Label(inspector_frame, text=f"X4:", background=style.lookup("header.TFrame", "background"))
]

inspector_labels_y = [
    Label(inspector_frame, text=f"Y1:", background=style.lookup("header.TFrame", "background")),
    Label(inspector_frame, text=f"Y2:", background=style.lookup("header.TFrame", "background")),
    Label(inspector_frame, text=f"Y3:", background=style.lookup("header.TFrame", "background")),
    Label(inspector_frame, text=f"Y4:", background=style.lookup("header.TFrame", "background"))
]

inspector_vars_x = [StringVar() for _ in range(4)]
inspector_vars_y = [StringVar() for _ in range(4)]

validate_is_number_cmd = (inspector_frame.register(validate_is_number),"%P")

inspector_entries_x = [
    Entry(inspector_frame, width=10, textvariable=inspector_vars_x[0],validate="key",validatecommand=validate_is_number_cmd),
    Entry(inspector_frame, width=10, textvariable=inspector_vars_x[1],validate="key",validatecommand=validate_is_number_cmd),
    Entry(inspector_frame, width=10, textvariable=inspector_vars_x[2],validate="key",validatecommand=validate_is_number_cmd),
    Entry(inspector_frame, width=10, textvariable=inspector_vars_x[3],validate="key",validatecommand=validate_is_number_cmd)
]

inspector_entries_y = [
    Entry(inspector_frame, width=10, textvariable=inspector_vars_y[0],validate="key",validatecommand=validate_is_number_cmd),
    Entry(inspector_frame, width=10, textvariable=inspector_vars_y[1],validate="key",validatecommand=validate_is_number_cmd),
    Entry(inspector_frame, width=10, textvariable=inspector_vars_y[2],validate="key",validatecommand=validate_is_number_cmd),
    Entry(inspector_frame, width=10, textvariable=inspector_vars_y[3],validate="key",validatecommand=validate_is_number_cmd)
]

for entry in inspector_entries_x + inspector_entries_y:
    entry.bind("<Return>", process_inspector_menu)

def update_inspector_entries(num_pairs):
    window.shown_inspector_entries = num_pairs
    for i in range(4):
        if i < num_pairs:
            smart_place(inspector_labels_x[i],(30,50+i*30),(30,50+i*30))
            smart_place(inspector_entries_x[i],(60,50+i*30),(60,50+i*30))
            smart_place(inspector_labels_y[i],(150,50+i*30),(150,50+i*30))
            smart_place(inspector_entries_y[i],(180,50+i*30),(180,50+i*30))
        else:
            inspector_labels_x[i].place_forget()
            inspector_entries_x[i].place_forget()
            inspector_labels_y[i].place_forget()
            inspector_entries_y[i].place_forget()

window.shown_inspector_entries = 0
update_inspector_entries(window.shown_inspector_entries)

trash_img = Image.open("images/trash.png")
trash_img = trash_img.resize((20,20))
trash_photo = ImageTk.PhotoImage(trash_img,master=inspector_frame)
inspector_delete_button = Button(inspector_frame,image=trash_photo,command=delete_connector_or_node) 
inspector_delete_button.trash_photo = trash_photo
smart_place(inspector_delete_button,(10,10),(10,10))

line_img = Image.open("images/line.png")
line_img = line_img.resize((20,20))
line_photo = ImageTk.PhotoImage(line_img,master=inspector_frame)
inspector_line_button = Button(inspector_frame,image=line_photo,command=turn_selected_connectors_into_lines)
inspector_line_button.line_photo = line_photo
smart_place(inspector_line_button,(60,10),(70,10))

bezier_img = Image.open("images/bezier.png")
bezier_img = bezier_img.resize((20,20))
bezier_photo = ImageTk.PhotoImage(bezier_img,master=inspector_frame)
inspector_bezier_button = Button(inspector_frame,image=bezier_photo,command=turn_selected_connectors_into_beziers)
inspector_bezier_button.bezier_photo = bezier_photo
smart_place(inspector_bezier_button,(110,10),(130,10))

circle_img = Image.open("images/circle.png")
circle_img = circle_img.resize((20,20))
circle_photo = ImageTk.PhotoImage(circle_img,master=inspector_frame)
inspector_circle_button = Button(inspector_frame,image=circle_photo,command=turn_selected_connectors_into_half_circles)
inspector_circle_button.circle_photo = circle_photo
smart_place(inspector_circle_button,(160,10),(190,10))

editor_group_listbox = Listbox(inspector_frame,width=43,height=5,bg=style.lookup("header.TFrame","background"),highlightcolor=style.lookup("hightlight.TListbox","background"))
editor_group_listbox.bind('<Double-1>', on_group_double_click)
smart_place(editor_group_listbox,(10,200),(10,200))

plus_img = Image.open("images/plus.png")
plus_img = plus_img.resize((20,20))
plus_photo = ImageTk.PhotoImage(plus_img,master=inspector_frame)
editor_new_group_button = Button(inspector_frame,image=plus_photo,command=open_group_selector)
editor_new_group_button.plus_photo = plus_photo
smart_place(editor_new_group_button,(10,165),(10,165))

trash_img = Image.open("images/trash.png")
trash_img = trash_img.resize((20,20))
trash_photo = ImageTk.PhotoImage(trash_img,master=inspector_frame)
editor_delete_group_button = Button(inspector_frame,image=trash_photo,command=delete_group_button) 
editor_delete_group_button.trash_photo = trash_photo
smart_place(editor_delete_group_button,(60,165),(70,165))

editor_extra_options_frame = Frame(editor_frame,height=40,width=992,style="header.TFrame")
smart_place(editor_extra_options_frame,(5,655),(5,655))

show_nodes_var = BooleanVar(value=True)
editor_show_nodes_checkbox = Checkbutton(editor_extra_options_frame,text="Draw Nodes",variable=show_nodes_var,command=on_toggle_draw_nodes)
smart_place(editor_show_nodes_checkbox,(10,10),(10,10))

rotation_var = StringVar(editor_extra_options_frame)
valid_angle_cmd = (editor_extra_options_frame.register(validate_angle),"%P")
editor_rotation_degrees_entry_box = Entry(editor_extra_options_frame,validate="key",validatecommand=valid_angle_cmd,textvariable=rotation_var,width=8)
smart_place(editor_rotation_degrees_entry_box,(170,10),(170,10))

undo_img = Image.open("images/undo.png")
undo_img = undo_img.resize((20,20))
undo_photo = ImageTk.PhotoImage(undo_img,master=editor_extra_options_frame)
editor_rotate_left_button = Button(editor_extra_options_frame,image=undo_photo,command=rotate_left) 
editor_rotate_left_button.undo_photo = undo_photo
smart_place(editor_rotate_left_button,(240,5),(260,5))

redo_img = Image.open("images/redo.png")
redo_img = redo_img.resize((20,20))
redo_photo = ImageTk.PhotoImage(redo_img,master=editor_extra_options_frame)
editor_rotate_right_button = Button(editor_extra_options_frame,image=redo_photo,command=rotate_right) 
editor_rotate_right_button.redo_photo = redo_photo
smart_place(editor_rotate_right_button,(280,5),(320,5))

center_x_label = Label(editor_extra_options_frame, text=f"Center X:", background=style.lookup("header.TFrame", "background"))
center_y_label = Label(editor_extra_options_frame, text=f"Y:", background=style.lookup("header.TFrame", "background"))
center_x_var = StringVar(editor_extra_options_frame)
center_y_var = StringVar(editor_extra_options_frame)
on_center_change_x_cmd = (editor_extra_options_frame.register(on_center_change_x),"%P")
on_center_change_y_cmd = (editor_extra_options_frame.register(on_center_change_y),"%P")
center_x_entry = Entry(editor_extra_options_frame,validate="key",validatecommand=on_center_change_x_cmd,textvariable=center_x_var,width=8)
center_y_entry = Entry(editor_extra_options_frame,validate="key",validatecommand=on_center_change_y_cmd,textvariable=center_y_var,width=8)
smart_place(center_x_label,(320,10),(390,10))
smart_place(center_x_entry,(380,10),(460,10))
smart_place(center_y_label,(440,10),(550,10))
smart_place(center_y_entry,(460,10),(580,10))


mirror_y_img = Image.open("images/mirror_y_axis.png")
mirror_y_img = mirror_y_img.resize((20,20))
mirror_y_photo = ImageTk.PhotoImage(mirror_y_img,master=editor_extra_options_frame)
editor_mirror_y_axis_button = Button(editor_extra_options_frame,image=mirror_y_photo,command=mirror_y) 
editor_mirror_y_axis_button.mirror_y_photo = mirror_y_photo
smart_place(editor_mirror_y_axis_button,(600,5),(700,5))

mirror_x_img = Image.open("images/mirror_x_axis.png")
mirror_x_img = mirror_x_img.resize((20,20))
mirror_x_photo = ImageTk.PhotoImage(mirror_x_img,master=editor_extra_options_frame)
editor_mirror_x_axis_button = Button(editor_extra_options_frame,image=mirror_x_photo,command=mirror_x) 
editor_mirror_x_axis_button.mirror_x_photo = mirror_x_photo
smart_place(editor_mirror_x_axis_button,(640,5),(770,5))

#__________________________________CONFIG____________________________________________
config_frame = Frame(window,height=700,width=1000,style="secondary.TFrame")

config_header_frame = Frame(config_frame,height=40,width=704,style="header.TFrame")
config_selected_label = Label(config_header_frame,font=('Helvetica',15),background="#9e9d9d",textvariable=config_txt_selected_label)
config_selected_label.letter = ""
config_selected_label.language = ""
config_selected_label.saved = None
smart_place(config_selected_label,(5,7),(5,7))
smart_place(config_header_frame,(5,0),(5,0))

positioning_canvas = letter.PositioningCanvas(Canvas(config_frame,width=700,height=600,background="#525252"))
smart_place(positioning_canvas.canvas,(5,45),(5,45))

positioning_canvas.canvas.create_image(0,0,image=grid_photo,anchor="nw",tags="grid")
positioning_canvas.canvas.create_image(0,0,image=grid_photo,anchor="nw",tags=["grid","base"])
positioning_canvas.canvas.create_line(350-200,300-200,350+200,300-200,fill="gray",tags="grid")
positioning_canvas.canvas.create_line(350-200,300+200,350+200,300+200,fill="gray",tags="grid")
positioning_canvas.canvas.create_line(350-200,300-200,350-200,300+200,fill="gray",tags="grid")
positioning_canvas.canvas.create_line(350+200,300-200,350+200,300+200,fill="gray",tags="grid")
positioning_canvas.grid_photo = grid_photo

config_inspector_frame = Frame(config_frame, width=282, height=300, style="header.TFrame")
smart_place(config_inspector_frame,(715,45),(715,45))

config_inspector_labels_x = [
    Label(config_inspector_frame, text=f"X:", background=style.lookup("header.TFrame", "background")),
    Label(config_inspector_frame, text=f"Width:", background=style.lookup("header.TFrame", "background")),
]

config_inspector_labels_y = [
    Label(inspector_frame, text=f"Y:", background=style.lookup("header.TFrame", "background")),
    Label(inspector_frame, text=f"Height:", background=style.lookup("header.TFrame", "background"))
]

config_inspector_vars_x = [StringVar() for _ in range(2)]
config_inspector_vars_y = [StringVar() for _ in range(2)]

config_inspector_entries_x = [
    Entry(config_inspector_frame, width=10, textvariable=config_inspector_vars_x[0],validate="key",validatecommand=validate_is_number_cmd),
    Entry(config_inspector_frame, width=10, textvariable=config_inspector_vars_x[1],validate="key",validatecommand=validate_is_number_cmd),
]

config_inspector_entries_y = [
    Entry(config_inspector_frame, width=10, textvariable=config_inspector_vars_y[0],validate="key",validatecommand=validate_is_number_cmd),
    Entry(config_inspector_frame, width=10, textvariable=config_inspector_vars_y[1],validate="key",validatecommand=validate_is_number_cmd)
]

for entry in config_inspector_entries_x + config_inspector_entries_y:
    entry.bind("<Return>", process_config_inspector_menu)

def config_update_inspector_entries(num_pairs):
    window.shown_inspector_entries = num_pairs
    for i in range(2):
        if i < num_pairs:
            smart_place(config_inspector_labels_x[i],(30,50+i*30),(30,50+i*30))
            smart_place(config_inspector_entries_x[i],(60,50+i*30),(60,50+i*30))
            smart_place(config_inspector_labels_y[i],(150,50+i*30),(150,50+i*30))
            smart_place(config_inspector_entries_y[i],(180,50+i*30),(180,50+i*30))
        else:
            config_inspector_labels_x[i].place_forget()
            config_inspector_entries_x[i].place_forget()
            config_inspector_labels_y[i].place_forget()
            config_inspector_entries_y[i].place_forget()

window.config_shown_inspector_entries = 0
update_inspector_entries(window.config_shown_inspector_entries)

config_inspector_delete_button = Button(config_inspector_frame,image=trash_photo,command=delete_letter_space) 
config_inspector_delete_button.trash_photo = trash_photo
smart_place(config_inspector_delete_button,(10,10),(10,10))

config_canvas_zoom_slider = Scale(config_inspector_frame,from_=100,to=400,value=100,length=180,variable=config_canvas_zoom_intvar,command=on_zoom_slider_change)
config_canvas_zoom_entry = Entry(config_inspector_frame,width=10,textvariable=config_canvas_zoom_stringvar,validate="key",validatecommand=validate_is_number_cmd)
smart_place(config_canvas_zoom_slider,(10,250),(10,250))
smart_place(config_canvas_zoom_entry,(200,250),(200,250))

config_turn_into_template_button = Button(config_inspector_frame,text="Clear Letter",command=config_canvas_unload_letter)
config_load_slots_button = Button(config_inspector_frame,text="Load Positioning",command=lambda:open_positioning_window(True))
smart_place(config_turn_into_template_button,(10,200),(10,200))
smart_place(config_load_slots_button,(100,200),(100,200))


editor_frame.lift()
config_frame.lower()

def reopen_debug_window_on_close():
    debug.revive()
    del registered["debug"]
    register("debug",debug.root)
    debug.debug_window.root.protocol("WM_DELETE_WINDOW", reopen_debug_window_on_close)

debug.init(window)
debug.debug_window.root.protocol("WM_DELETE_WINDOW", reopen_debug_window_on_close)


register("debug",debug.root)
register("main",window)