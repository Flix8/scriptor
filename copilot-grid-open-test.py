# Test script: Scrollable grid of buttons with images and labels in tkinter

import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

root = tk.Tk()
root.title("Scrollable Grid Test")
root.geometry("500x400")

# Create canvas and scrollbar
canvas = tk.Canvas(root)
scrollbar = ttk.Scrollbar(root, orient="vertical", command=canvas.yview)
canvas.configure(yscrollcommand=scrollbar.set)

scrollbar.pack(side="right", fill="y")
canvas.pack(side="left", fill="both", expand=True)

# Create a frame inside the canvas
frame = tk.Frame(canvas)
canvas.create_window((0, 0), window=frame, anchor="nw")

def on_frame_configure(event):
    canvas.configure(scrollregion=canvas.bbox("all"))

frame.bind("<Configure>", on_frame_configure)

# Dummy image (colored square)
def create_dummy_image(color):
    img = Image.new("RGB", (90, 90), color)
    return ImageTk.PhotoImage(img)

# Add grid of buttons
num_rows = 8
num_cols = 4
colors = ["red", "green", "blue", "orange", "purple", "yellow", "cyan", "magenta"]

for row in range(num_rows):
    for col in range(num_cols):
        letter_name = f"Letter {row*num_cols + col + 1}"
        color = colors[(row*num_cols + col) % len(colors)]
        img = create_dummy_image(color)
        btn = tk.Button(frame, text=letter_name, image=img, compound="top",
                        command=lambda name=letter_name: print(f"Clicked {name}"))
        btn.image = img  # Prevent garbage collection
        btn.grid(row=row, column=col, padx=10, pady=10)

root.mainloop()