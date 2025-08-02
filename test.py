import tkinter as tk
from tkinter import ttk

root = tk.Tk()
tree = ttk.Treeview(root)

# Add root item
parent = tree.insert('', 'end', text='Player')

# Add children
tree.insert(parent, 'end', text='Camera')
tree.insert(parent, 'end', text='Weapon')

# Add another root-level item
enemy = tree.insert('', 'end', text='Enemy')
tree.insert(enemy, 'end', text='AI')
tree.insert(enemy, 'end', text='Health')

dragging_item = None

def on_button_press(event):
    global dragging_item
    item = tree.identify_row(event.y)
    if item:
        dragging_item = item

def on_button_release(event):
    global dragging_item
    if not dragging_item:
        return
    target = tree.identify_row(event.y)
    if target and target != dragging_item:
        tree.move(dragging_item, target, 'end')
    dragging_item = None

tree.bind("<ButtonPress-1>", on_button_press)
tree.bind("<ButtonRelease-1>", on_button_release)

tree.pack(expand=True, fill='both')
root.mainloop()