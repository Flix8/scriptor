import tkinter as tk
from tkinter import ttk

def populate_treeview():
    # Add items with custom background colors
    tree.insert("", "end", text="Item 1", tags=("red",))
    tree.insert("", "end", text="Item 2", tags=("green",))
    tree.insert("", "end", text="Item 3", tags=("blue",))
    tree.insert("", "end", text="Item 4", tags=("yellow",))

root = tk.Tk()
root.geometry("300x200")

# Create a Treeview widget
tree = ttk.Treeview(root, show="tree")
tree.pack(fill=tk.BOTH, expand=True)

# Define tag styles for custom row backgrounds
tree.tag_configure("red", background="red")
tree.tag_configure("green", background="green")
tree.tag_configure("blue", background="blue")
tree.tag_configure("yellow", background="yellow")

# Populate the Treeview with items
populate_treeview()

root.mainloop()