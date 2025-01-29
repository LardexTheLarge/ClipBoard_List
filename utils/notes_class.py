import os
import tkinter as tk
from tkinter import messagebox

class NoteTakerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Note Taker")

        # Create a directory to store notes if it doesn't exist
        if not os.path.exists("notes"):
            os.makedirs("notes")

        # GUI Elements
        self.title_label = tk.Label(root, text="Title:")
        self.title_label.grid(row=0, column=0, padx=10, pady=10)

        self.title_entry = tk.Entry(root, width=50)
        self.title_entry.grid(row=0, column=1, padx=10, pady=10)

        self.note_label = tk.Label(root, text="Note:")
        self.note_label.grid(row=1, column=0, padx=10, pady=10)

        self.note_text = tk.Text(root, width=50, height=20)
        self.note_text.grid(row=1, column=1, padx=10, pady=10)

        self.save_button = tk.Button(root, text="Save Note", command=self.save_note)
        self.save_button.grid(row=2, column=1, padx=10, pady=10, sticky=tk.E)

        self.load_button = tk.Button(root, text="Load Note", command=self.load_note)
        self.load_button.grid(row=2, column=1, padx=10, pady=10, sticky=tk.W)

    def save_note(self):
        """Saves the note to a file with the given title."""
        title = self.title_entry.get()
        content = self.note_text.get("1.0", tk.END)

        if not title:
            messagebox.showwarning("Warning", "Please enter a title for the note.")
            return

        # Save the note as a text file
        with open(f"notes/{title}.txt", "w") as file:
            file.write(content)

        messagebox.showinfo("Success", "Note saved successfully!")
        self.title_entry.delete(0, tk.END)
        self.note_text.delete("1.0", tk.END)

    def load_note(self):
        """Loads a note from a file based on the given title."""
        title = self.title_entry.get()

        if not title:
            messagebox.showwarning("Warning", "Please enter a title to load the note.")
            return

        try:
            with open(f"notes/{title}.txt", "r") as file:
                content = file.read()
                self.note_text.delete("1.0", tk.END)
                self.note_text.insert("1.0", content)
        except FileNotFoundError:
            messagebox.showwarning("Warning", "Note not found.")
