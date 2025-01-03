import subprocess
import os
from tkinter import *
from tkinter import messagebox
from tkinter.ttk import *
import tkinter.font as font
from PIL import Image, ImageTk

import debug_console as debug
import letter_core as letter
#________GENERAL FUNCTIONS______________
registered = {}
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

window = Tk()
#Style
style = Style(window)
style.configure("secondary.TFrame", background="#1a1919")
style.configure("toolbar.TFrame", background="#4a4949")
style.configure("header.TFrame", background="#9e9d9d")

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

editor_header_frame = Frame(window,height=40,width=700,style="header.TFrame")
selected_label = Label(editor_header_frame,text="Selected: Placeholder [Placeholder]",font=('Helvetica',15),background="#9e9d9d")
selected_label.place(x=5,y=7)
editor_header_frame.place(x=0,y=60)

editor_canvas = letter.EditorCanvas(Canvas(window,width=700,height=600,background="#525252"))
editor_canvas.canvas.place(x=0,y=100)

grid_img = Image.open("images/grid.png")
grid_photo = ImageTk.PhotoImage(grid_img,master=window)
editor_canvas.canvas.create_image(0,0,image=grid_photo,anchor="nw",tags="grid")
editor_canvas.grid_photo = grid_photo


debug.init(window)

register("debug",debug.root)
register("main",window)