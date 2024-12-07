import tkinter as tk
from time import time, ctime
from tkinter.scrolledtext import ScrolledText


class DebugWindow:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Debug Window")
        
        # Scrolled text area for logs
        self.text_area = ScrolledText(self.root, wrap=tk.WORD, width=60, height=20)
        self.text_area.pack(expand=True, fill='both')
        self.text_area.configure(state='disabled')
        
        # Entry field for commands
        self.command_entry = tk.Entry(self.root, width=60)
        self.command_entry.pack(fill='x', pady=5)
        self.command_entry.bind("<Return>", self.process_command)

        self.root.withdraw()

        self.to_execute = ""

    def send(self, message):
        """Add a message to the text area."""
        self.text_area.configure(state='normal')
        self.text_area.insert(tk.END, message + "\n")
        self.text_area.see(tk.END)
        self.text_area.configure(state='disabled')

    def clear(self):
        """Clear the text area."""
        self.text_area.configure(state='normal')
        self.text_area.delete(1.0, tk.END)
        self.text_area.configure(state='disabled')

    def process_command(self, event):
        """Process the entered command."""
        command = self.command_entry.get()
        if command.strip():  # Avoid empty commands
            self.send(f"Trying to execute command: {command}")
            self.to_execute = command
            self.command_entry.delete(0, tk.END)  # Clear the entry field

def init(master):
    global debug_window, root
    root = tk.Toplevel(master=master)
    debug_window = DebugWindow(root)

def send(message):
    debug_window.send(message)
    with open("debug.log", "a") as file:
        file.write(f"[{ctime(time())}]: {message}\n")

def clear():
    debug_window.clear()

with open("debug.log", "w") as file:
    file.write("THIS LOG IS FOR DEBUGGING PURPOSES. THANK YOU.\n")
