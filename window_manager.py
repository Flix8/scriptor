import subprocess
import os
from tkinter import *
from tkinter import messagebox
from tkinter import simpledialog
from tkinter.ttk import *
import tkinter.font as font
from PIL import Image, ImageTk

import debug_console as debug
import letter_core as letter
import saving_agent as saving
#________GENERAL FUNCTIONS______________
registered = {}
language_selector_open = False
letter_selector_open = False
save_window_open = False
focused = 0
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
    focused = frame.id
    frame.tkraise()
#_______BUTTON FUNCTIONS________________
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

def open_language_selector():
    #Written by Copilot
    if not editor_canvas.saved:
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
    if not editor_canvas.saved:
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
            editor_canvas.load_letter(saving.load_letter(window.language_name,selected_letter,True),selected_letter)
            editor_canvas.saved = True
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
        selected_index = listbox.curselection()
        if selected_index:
            selected_letter = listbox.get(selected_index)
            for item in canvas.find_all():
                canvas.delete(item)
            letter.draw_letter(saving.load_letter(window.language_name,selected_letter,False),canvas,0.2,(75,75),False,None)

    def on_letter_double_click(event):
        selected_index = listbox.curselection()
        if selected_index:
            letter_name = listbox.get(selected_index)
            new_name = simpledialog.askstring("Rename Letter", "Enter new name:", initialvalue=letter_name)
            if new_name and new_name != letter_name:
                os.rename(os.path.join(letters_path, letter_name + ".json"),os.path.join(letters_path, new_name + ".json"))
                listbox.delete(selected_index)
                listbox.insert(selected_index, new_name)

            
    letter_selector_open = True
    letter_selector = Toplevel(window)
    register("letter_selector",letter_selector)
    letter_selector.title("Select Letter")
    letter_selector.geometry("300x450")
    letter_selector.protocol("WM_DELETE_WINDOW", close_letter_selector)

    canvas = Canvas(letter_selector, width=150, height=150, bg="white")
    canvas.pack(pady=10)

    listbox = Listbox(letter_selector)
    listbox.pack(fill=BOTH, expand=True, padx=10, pady=10)
    listbox.bind('<<ListboxSelect>>', on_letter_select)
    listbox.bind('<Double-1>', on_letter_double_click)

    letters_path = os.path.join("languages", language, "letters")
    letters = [f for f in os.listdir(letters_path) if os.path.isfile(os.path.join(letters_path, f))]
    for let in letters:
        listbox.insert(END, os.path.splitext(let)[0])

    button_frame = Frame(letter_selector)
    button_frame.pack(fill=X, padx=10, pady=10)

    open_button = Button(button_frame, text="Open", command=on_open)
    open_button.pack(side=LEFT, padx=5)

    close_button = Button(button_frame, text="Close", command=on_close)
    close_button.pack(side=LEFT, padx=5)

def save_letter_selector():
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
        close("save_letter_selector")
        letter_selector_open = False

    def on_letter_select(event):
        selected_index = listbox.curselection()
        if selected_index:
            selected_letter = listbox.get(selected_index)
            entry.delete(0, END)
            entry.insert(0, selected_letter)

    letter_selector_open = True
    letter_selector = Toplevel(window)
    register("save_letter_selector",letter_selector)
    letter_selector.title("Save Letter")
    letter_selector.geometry("300x400")
    letter_selector.protocol("WM_DELETE_WINDOW", close_letter_selector)

    listbox = Listbox(letter_selector)
    listbox.pack(fill=BOTH, expand=True, padx=10, pady=10)
    listbox.bind('<<ListboxSelect>>', on_letter_select)

    letters_path = os.path.join("languages", language, "letters")
    letters = [f for f in os.listdir(letters_path) if os.path.isfile(os.path.join(letters_path, f))]
    for let in letters:
        listbox.insert(END, os.path.splitext(let)[0])

    entry_frame = Frame(letter_selector)
    entry_frame.pack(fill=X, padx=10, pady=10)

    entry_label = Label(entry_frame, text="Enter name:")
    entry_label.pack(side=LEFT, padx=5)

    entry = Entry(entry_frame)
    entry.pack(fill=X, expand=True, padx=5)

    button_frame = Frame(letter_selector)
    button_frame.pack(fill=X, padx=10, pady=10)

    save_button = Button(button_frame, text="Save", command=on_save)
    save_button.pack(side=LEFT, padx=5)

    cancel_button = Button(button_frame, text="Cancel", command=on_cancel)
    cancel_button.pack(side=LEFT, padx=5)

def ask_save(action="new"):
    global save_window_open

    if save_window_open:
        print("RET HERE")
        return
    def on_save():
        save_letter_selector()
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
    if not editor_canvas.saved:
        ask_save("new")
        return
    editor_canvas.saved = True
    new_letter = letter.Letter()
    new_letter.segments.append(letter.Segment())
    editor_canvas.load_letter(new_letter,"Unnamed")

def process_config_menu(event):
    #Check if anything was changed
    change = False
    for i,entry_x,var_x,entry_y,var_y in zip(range(4),config_entries_x,config_vars_x,config_entries_y,config_vars_y):
        if i >= window.shown_config_entries:
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
            dx = float(config_entries_x[0].get()) - float(config_entries_x[0].original_value)
            dy = float(config_entries_y[0].get()) - float(config_entries_y[0].original_value)
            for node in editor_canvas.letter.segments[editor_canvas.selected_segment].nodes:
                if node.selected:
                    node.x += dx
                    node.y += dy
        elif editor_canvas.selection_type == "connector":
            for i,connector in enumerate(editor_canvas.letter.segments[editor_canvas.selected_segment].connectors):
                if connector.selected:
                    node1 = editor_canvas.letter.segments[editor_canvas.selected_segment].nodes[i]
                    node2 = editor_canvas.letter.segments[editor_canvas.selected_segment].nodes[(i+1)%len(editor_canvas.letter.segments[editor_canvas.selected_segment].connectors)]
                    node1.x = float(config_entries_x[0].get())
                    node1.y = float(config_entries_y[0].get())
                    node2.x = float(config_entries_x[1].get())
                    node2.y = float(config_entries_y[1].get())
                    if connector.type == "BEZIER":
                        connector.anchors[0].x = float(config_entries_x[2].get())
                        connector.anchors[0].y = float(config_entries_y[2].get())
                        connector.anchors[1].x = float(config_entries_x[3].get())
                        connector.anchors[1].y = float(config_entries_y[3].get())
                    break

        editor_canvas.update()
window = Tk()
window.language_name = ""
#Tk Variables
txt_selected_label = StringVar(window)
txt_selected_label.set("Selected: Placeholder [Placeholder]")
#Style
style = Style(window)
style.configure("secondary.TFrame", background="#1a1919")
style.configure("toolbar.TFrame", background="#4a4949")
style.configure("header.TFrame", background="#9e9d9d")
style.configure("highlight.TListbox", background="#bfbfbf")

window.geometry("1000x800")
background = Frame(window,width=1000,height=800,style="secondary.TFrame")
background.pack()
background.lift()

window.lift()
window.title("Scriptor - Letter Editor")

toolbar_frame = Frame(window,height=40,width=500,style="toolbar.TFrame")
new_button = Button(toolbar_frame, text="New",width=10,command=lambda: create_new_letter())
save_button = Button(toolbar_frame, text="Save",width=10,command=save_letter_selector)
open_button = Button(toolbar_frame, text="Open",width=10,command=open_letter_selector)
settings_button = Button(toolbar_frame, text="Settings",width=10,command=lambda: print("SETTINGS"))
language_button = Button(toolbar_frame, text="Language",width=10,command=open_language_selector)
new_button.place(x=20,y=7)
save_button.place(x=100,y=7)
open_button.place(x=180,y=7)
settings_button.place(x=260,y=7)
language_button.place(x=340,y=7)
toolbar_frame.place(x=20,y=0)

navigation_frame = Frame(window,height=50,width=300,style="toolbar.TFrame")
edit_button = Button(navigation_frame, text="Edit",width=10,command=lambda: print("EDIT"))
configure_button = Button(navigation_frame, text="Configure",width=10,command=lambda: print("CONFIGURE"))
write_button = Button(navigation_frame, text="Write",width=10,command=lambda: print("WRITE"))
write_button.place(x=20,y=7)
edit_button.place(x=120,y=7)
configure_button.place(x=220,y=7)
navigation_frame.place(x=700,y=0)

editor_frame = Frame(window,height=700,width=1000,style="secondary.TFrame")

editor_header_frame = Frame(editor_frame,height=40,width=700,style="header.TFrame")
editor_selected_label = Label(editor_header_frame,font=('Helvetica',15),background="#9e9d9d",textvariable=txt_selected_label)
editor_selected_label.letter = ""
editor_selected_label.language = ""
editor_selected_label.saved = None
editor_selected_label.place(x=5,y=7)
editor_frame.place(x=0,y=60)
editor_header_frame.place(x=0,y=0)

editor_canvas = letter.EditorCanvas(Canvas(editor_frame,width=700,height=600,background="#525252"))
editor_canvas.canvas.place(x=0,y=40)

editor_segment_listbox_frame = Frame(editor_frame,width=282,height=300,style="header.TFrame")
editor_segment_listbox_frame.place(x=710,y=344)

editor_segment_listbox = Listbox(editor_segment_listbox_frame,width=43,height=15,bg=style.lookup("header.TFrame","background"),highlightcolor=style.lookup("hightlight.TListbox","background"))
editor_segment_listbox.bind('<<ListboxSelect>>', on_segment_select)
editor_segment_listbox.bind('<Double-1>', on_segment_double_click)
editor_segment_listbox.place(x=10,y=45)

plus_img = Image.open("images/plus.png")
plus_img = plus_img.resize((20,20))
plus_photo = ImageTk.PhotoImage(plus_img,master=editor_segment_listbox_frame)
editor_new_segment_button = Button(editor_segment_listbox_frame,image=plus_photo,command=new_segment_button)
editor_new_segment_button.plus_photo = plus_photo
editor_new_segment_button.place(x=10,y=10)

trash_img = Image.open("images/trash.png")
trash_img = trash_img.resize((20,20))
trash_photo = ImageTk.PhotoImage(trash_img,master=editor_segment_listbox_frame)
editor_delete_segment_button = Button(editor_segment_listbox_frame,image=trash_photo,command=delete_segment_button) 
editor_delete_segment_button.trash_photo = trash_photo
editor_delete_segment_button.place(x=60,y=10)

grid_img = Image.open("images/grid.png")
grid_photo = ImageTk.PhotoImage(grid_img,master=window)
editor_canvas.canvas.create_image(0,0,image=grid_photo,anchor="nw",tags="grid")
editor_canvas.grid_photo = grid_photo

configuration_frame = Frame(editor_frame, width=282, height=300, style="header.TFrame")
configuration_frame.place(x=710, y=40)

config_labels_x = [
    Label(configuration_frame, text=f"X1:", background=style.lookup("header.TFrame", "background")),
    Label(configuration_frame, text=f"X2:", background=style.lookup("header.TFrame", "background")),
    Label(configuration_frame, text=f"X3:", background=style.lookup("header.TFrame", "background")),
    Label(configuration_frame, text=f"X4:", background=style.lookup("header.TFrame", "background"))
]

config_labels_y = [
    Label(configuration_frame, text=f"Y1:", background=style.lookup("header.TFrame", "background")),
    Label(configuration_frame, text=f"Y2:", background=style.lookup("header.TFrame", "background")),
    Label(configuration_frame, text=f"Y3:", background=style.lookup("header.TFrame", "background")),
    Label(configuration_frame, text=f"Y4:", background=style.lookup("header.TFrame", "background"))
]

config_vars_x = [StringVar() for _ in range(4)]
config_vars_y = [StringVar() for _ in range(4)]

config_entries_x = [
    Entry(configuration_frame, width=10, textvariable=config_vars_x[0]),
    Entry(configuration_frame, width=10, textvariable=config_vars_x[1]),
    Entry(configuration_frame, width=10, textvariable=config_vars_x[2]),
    Entry(configuration_frame, width=10, textvariable=config_vars_x[3])
]

config_entries_y = [
    Entry(configuration_frame, width=10, textvariable=config_vars_y[0]),
    Entry(configuration_frame, width=10, textvariable=config_vars_y[1]),
    Entry(configuration_frame, width=10, textvariable=config_vars_y[2]),
    Entry(configuration_frame, width=10, textvariable=config_vars_y[3])
]

for entry in config_entries_x + config_entries_y:
    entry.bind("<Return>", process_config_menu)

def update_configuration_entries(num_pairs):
    window.shown_config_entries = num_pairs
    for i in range(4):
        if i < num_pairs:
            config_labels_x[i].place(x=30, y=10 + i * 30)
            config_entries_x[i].place(x=60, y=10 + i * 30)
            config_labels_y[i].place(x=150, y=10 + i * 30)
            config_entries_y[i].place(x=180, y=10 + i * 30)
        else:
            config_labels_x[i].place_forget()
            config_entries_x[i].place_forget()
            config_labels_y[i].place_forget()
            config_entries_y[i].place_forget()

window.shown_config_entries = 0
update_configuration_entries(window.shown_config_entries)

debug.init(window)

register("debug",debug.root)
register("main",window)