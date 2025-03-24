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
        self.command_log = []
        self.cur_pos_in_log = None
        self.command_entry = tk.Entry(self.root, width=60)
        self.command_entry.pack(fill='x', pady=5)
        self.command_entry.bind("<Return>", self.process_command)
        self.command_entry.bind("<Up>", self.move_up_log)
        self.command_entry.bind("<Down>", self.move_down_log)

        self.root.withdraw()

        self.to_execute = []

    def send(self, message):
        """Add a message to the text area."""
        self.text_area.configure(state='normal')
        self.text_area.insert(tk.END, message + "\n")
        self.text_area.see(tk.END)
        self.text_area.configure(state='disabled')
        with open("debug.log", "a") as file:
            file.write(f"[{ctime(time())}]: {message}\n")

    def clear(self):
        """Clear the text area."""
        self.text_area.configure(state='normal')
        self.text_area.delete(1.0, tk.END)
        self.text_area.configure(state='disabled')
    def move_up_log(self,event):
        if len(self.command_log) == 0:
            return
        if self.cur_pos_in_log == None:
            self.cur_pos_in_log = 0
        elif self.cur_pos_in_log < len(self.command_log)-1:
            self.cur_pos_in_log += 1
        self.command_entry.delete(0,tk.END)
        self.command_entry.insert(0,self.command_log[self.cur_pos_in_log])
    def move_down_log(self,event):
        if self.cur_pos_in_log == None:
            return
        elif self.cur_pos_in_log == 0:
            self.command_entry.delete(0,tk.END)
            self.cur_pos_in_log = None
            return
        else:
            self.cur_pos_in_log -= 1
        self.command_entry.delete(0,tk.END)
        self.command_entry.insert(0,self.command_log[self.cur_pos_in_log])        
    def process_command(self, event):
        """Process the entered command."""
        self.cur_pos_in_log = None
        command = self.command_entry.get()
        if command.strip():  # Avoid empty commands
            self.command_log.insert(0,command)
            if len(self.command_log) > 36:
                self.command_log.pop()
            self.send(f"Trying to execute command: {command}")
            self.to_execute.append(command)
            self.command_entry.delete(0, tk.END)  # Clear the entry field

def init(master):
    global debug_window, root
    root = tk.Toplevel(master=master)
    debug_window = DebugWindow(root)

def revive():
    master = debug_window.root.master
    debug_window.root.destroy()
    init(master)

def send(*args):
    # Changed by ChatGPT to work with any amount of args.
    message = ";".join(map(str, args))
    debug_window.send(message)

def clear():
    debug_window.clear()

with open("debug.log", "w") as file:
    file.write("THIS LOG IS FOR DEBUGGING PURPOSES. THANK YOU.\n")
