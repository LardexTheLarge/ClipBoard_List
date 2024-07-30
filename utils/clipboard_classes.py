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

        self.listbox = tk.Listbox(root, width=100, height=20)
        self.listbox.pack(pady=20)

        self.refresh_button = tk.Button(root, text="Refresh", command=self.refresh_list)
        self.refresh_button.pack(pady=10)

        self.select_button = tk.Button(root, text="Select", command=self.select_text)
        self.select_button.pack(pady=10)

        self.refresh_list()

    def refresh_list(self):
        self.listbox.delete(0, tk.END)
        for item in self.clipboard_manager.get_history():
            self.listbox.insert(tk.END, item)

    def select_text(self):
        selected_text = self.listbox.get(tk.ACTIVE)
        if selected_text:
            pyperclip.copy(selected_text)
            messagebox.showinfo("Clipboard Manager", "Text copied to clipboard!")
        else:
            messagebox.showwarning("Clipboard Manager", "No text selected!") 