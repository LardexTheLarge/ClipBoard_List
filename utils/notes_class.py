import os
import tkinter as tk
from tkinter import messagebox, ttk
from utils.theme_manager_classes import ThemeManager  # Import the ThemeManager class

class NoteTakerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Note Taker")

        # Initialize ThemeManager
        self.theme_manager = ThemeManager()

        # Create a directory to store notes if it doesn't exist
        if not os.path.exists("notes"):
            os.makedirs("notes")

        # Configure grid weights for responsive layout
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_columnconfigure(2, weight=1)
        self.root.grid_columnconfigure(3, weight=1)
        self.root.grid_rowconfigure(1, weight=1)  # Allow the text area to expand

        # Dropdown for available notes
        self.title_entry = ttk.Combobox(root, width=47)
        self.title_entry.grid(row=0, column=0, padx=10, pady=10, columnspan=4, sticky="ew")  # Span across all columns
        self.title_entry.bind("<<ComboboxSelected>>", self.load_note_from_dropdown)
        self.update_note_dropdown()

        # Note text area
        self.note_text = tk.Text(root, width=50, height=20)
        self.note_text.grid(row=1, column=0, padx=10, pady=10, columnspan=4, sticky="nsew")  # Span across all columns

        # Buttons in one row, responsive to window size
        self.save_button = tk.Button(root, text="Save Note", command=self.save_note)
        self.save_button.grid(row=2, column=0, padx=5, pady=10, sticky="ew")

        self.load_button = tk.Button(root, text="Load Note", command=self.load_note)
        self.load_button.grid(row=2, column=1, padx=5, pady=10, sticky="ew")

        self.delete_button = tk.Button(root, text="Delete Note", command=self.delete_note)
        self.delete_button.grid(row=2, column=2, padx=5, pady=10, sticky="ew")

        self.theme_button = tk.Button(root, text="Toggle Theme", command=self.toggle_theme)
        self.theme_button.grid(row=2, column=3, padx=5, pady=10, sticky="ew")

        # Apply the default theme (dark)
        self.theme_manager.apply_theme(root, self.theme_manager.current_theme)

    def update_note_dropdown(self):
        """Updates the dropdown list with available notes."""
        notes = [f.replace(".txt", "") for f in os.listdir("notes") if f.endswith(".txt")]
        self.title_entry["values"] = notes

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
        self.update_note_dropdown()  # Update the dropdown after saving

    def load_note(self):
        """Loads a note from a file based on the given title."""
        title = self.title_entry.get()

        if not title:
            messagebox.showwarning("Warning", "Please enter a title to load the note.")
            return

        self.load_note_by_title(title)

    def load_note_from_dropdown(self, event=None):
        """Loads a note when a title is selected from the dropdown."""
        title = self.title_entry.get()
        if title:
            self.load_note_by_title(title)

    def load_note_by_title(self, title):
        """Helper method to load a note by title."""
        try:
            with open(f"notes/{title}.txt", "r") as file:
                content = file.read()
                self.note_text.delete("1.0", tk.END)
                self.note_text.insert("1.0", content)
        except FileNotFoundError:
            messagebox.showwarning("Warning", "Note not found.")

    def delete_note(self):
        """Deletes a note file based on the selected title."""
        title = self.title_entry.get()

        if not title:
            messagebox.showwarning("Warning", "Please select a note to delete.")
            return

        # Confirm deletion with the user
        confirm = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete the note '{title}'?")
        if confirm:
            try:
                os.remove(f"notes/{title}.txt")
                messagebox.showinfo("Success", f"Note '{title}' deleted successfully!")
                self.title_entry.delete(0, tk.END)
                self.note_text.delete("1.0", tk.END)
                self.update_note_dropdown()  # Update the dropdown after deletion
            except FileNotFoundError:
                messagebox.showwarning("Warning", "Note not found.")

    def toggle_theme(self):
        """Toggles between light and dark themes."""
        self.theme_manager.toggle_theme(self.root)