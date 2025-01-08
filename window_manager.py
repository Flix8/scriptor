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
#________GENERAL FUNCTIONS______________
registered = {}
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
new_button = Button(toolbar_frame, text="New",width=10,command=lambda: print("NEW"))
save_button = Button(toolbar_frame, text="Save",width=10,command=lambda: print("SAVE"))
open_button = Button(toolbar_frame, text="Open",width=10,command=lambda: print("OPEN"))
settings_button = Button(toolbar_frame, text="Settings",width=10,command=lambda: print("SETTINGS"))
new_button.place(x=20,y=7)
save_button.place(x=100,y=7)
open_button.place(x=180,y=7)
settings_button.place(x=260,y=7)
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
editor_selected_label.place(x=5,y=7)
editor_frame.place(x=0,y=60)
editor_header_frame.place(x=0,y=0)

editor_canvas = letter.EditorCanvas(Canvas(editor_frame,width=700,height=600,background="#525252"))
editor_canvas.canvas.place(x=0,y=40)

editor_segment_listbox = Listbox(editor_frame,width=43,height=15,bg=style.lookup("header.TFrame","background"),highlightcolor=style.lookup("hightlight.TListbox","background"))
editor_segment_listbox.bind('<<ListboxSelect>>', on_segment_select)
editor_segment_listbox.bind('<Double-1>', on_segment_double_click)
editor_segment_listbox.place(x=720,y=400)

plus_img = Image.open("images/plus.png")
plus_img = plus_img.resize((20,20))
plus_photo = ImageTk.PhotoImage(plus_img,master=editor_frame)
editor_new_segment_button = Button(editor_frame,image=plus_photo,command=new_segment_button)
editor_new_segment_button.plus_photo = plus_photo
editor_new_segment_button.place(x=720,y=365)

trash_img = Image.open("images/trash.png")
trash_img = trash_img.resize((20,20))
trash_photo = ImageTk.PhotoImage(trash_img,master=editor_frame)
editor_delete_segment_button = Button(editor_frame,image=trash_photo,command=delete_segment_button) 
editor_delete_segment_button.trash_photo = trash_photo
editor_delete_segment_button.place(x=770,y=365)

grid_img = Image.open("images/grid.png")
grid_photo = ImageTk.PhotoImage(grid_img,master=window)
editor_canvas.canvas.create_image(0,0,image=grid_photo,anchor="nw",tags="grid")
editor_canvas.grid_photo = grid_photo


debug.init(window)

register("debug",debug.root)
register("main",window)