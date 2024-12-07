import subprocess
import os
import tkinter as tk
from tkinter import messagebox
import tkinter.font as font
from PIL import Image, ImageTk
#________GENERAL FUNCTIONS______________
registered = {}
def register(name,root:tk.Tk):
    global registered
    registered[name] = root
def close(name):
    registered[name].destroy()
    del registered[name]
def visibility(master:tk.Tk,visible:bool):
    if visible:
        master.deiconify()
        master.lift()
    else:
        master.withdraw()