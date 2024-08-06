import pyperclip
import time
import threading
import tkinter as tk
from tkinter import messagebox
import json
import os

class ClipboardManager:
    def __init__(self):
        self.clipboard_history = []
        self.history_file = "clipboard_history.json"
        self.load_history()

    def monitor_clipboard(self):
        previous_text = ""
        while True:
            current_text = pyperclip.paste()
            if current_text != previous_text and current_text not in self.clipboard_history:
                self.clipboard_history.append(current_text)
                self.save_history()
                previous_text = current_text
            time.sleep(1)

    def get_history(self):
        return self.clipboard_history

    def save_history(self):
        with open(self.history_file, 'w') as f:
            json.dump(self.clipboard_history, f)

    def load_history(self):
        if os.path.exists(self.history_file):
            with open(self.history_file, 'r') as f:
                self.clipboard_history = json.load(f)

class ClipboardApp:
    def __init__(self, root, clipboard_manager):
        self.root = root
        self.root.title("Clipboard Manager")
        self.clipboard_manager = clipboard_manager

        self.selected_label = None  # To keep track of the selected label

        self.grid_frame = tk.Frame(root)
        self.grid_frame.pack(pady=20)

        self.refresh_button = tk.Button(root, text="Refresh", command=self.refresh_grid)
        self.refresh_button.pack(pady=10)

        self.delete_button = tk.Button(root, text="Delete", command=self.delete_selected)
        self.delete_button.pack(pady=10)

        self.refresh_grid()  # Refresh the grid when the application starts

    def refresh_grid(self):
        for widget in self.grid_frame.winfo_children():
            widget.destroy()
        
        clipboard_history = self.clipboard_manager.get_history()
        num_columns = 3  # Set the number of columns in the grid
        for index, item in enumerate(clipboard_history):
            row = index // num_columns
            column = index % num_columns
            label = tk.Label(self.grid_frame, text=item, borderwidth=1, relief="solid", width=30, height=2, wraplength=250)
            label.grid(row=row, column=column, padx=5, pady=5)
            label.bind("<Double-Button-1>", lambda event, text=item: self.copy_text(text))
            label.bind("<Button-1>", lambda event, lbl=label: self.select_label(lbl))

        # Configure grid to expand with window size
        for column in range(num_columns):
            self.grid_frame.columnconfigure(column, weight=1)
        for row in range((len(clipboard_history) + num_columns - 1) // num_columns):
            self.grid_frame.rowconfigure(row, weight=1)

    def select_label(self, label):
        if self.selected_label:
            self.selected_label.config(bg="SystemButtonFace")
        self.selected_label = label
        label.config(bg="lightblue")

    def delete_selected(self):
        if self.selected_label:
            item_to_delete = self.selected_label.cget("text")
            self.clipboard_manager.clipboard_history.remove(item_to_delete)
            self.clipboard_manager.save_history()
            self.refresh_grid()
            self.selected_label = None
        else:
            messagebox.showwarning("Clipboard Manager", "No item selected!")

    def copy_text(self, text):
        if text:
            pyperclip.copy(text)
            messagebox.showinfo("Clipboard Manager", "Text copied to clipboard!")
        else:
            messagebox.showwarning("Clipboard Manager", "No text selected!")