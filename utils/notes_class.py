import os
import tkinter as tk
from tkinter import messagebox, ttk
import requests
from dotenv import load_dotenv
from utils.message_popup import MessagePopup
from utils.theme_manager_classes import ThemeManager  # Import the ThemeManager class

class NoteTakerApp:
    def __init__(self, root):
        self.root = root
        self.selected_label = None  # Track the currently selected note
        self.selected_note = None  # Track selected note title
        self.root.title("Note Taker")

        # Initialize ThemeManager
        self.theme_manager = ThemeManager()
        bg_color, fg_color, button_bg, button_fg = self.theme_manager.get_theme_colors(self.theme_manager.current_theme)

        # Apply dark blue background
        self.root.config(bg=bg_color)

        # Ensure there's only ONE main frame with the correct theme
        self.main_frame = tk.Frame(root)
        self.main_frame.pack(fill=tk.Y)

        # Buttons frame
        self.button_frame = tk.Frame(root, bg=bg_color)
        self.button_frame.pack(side=tk.BOTTOM, pady=10, anchor=tk.CENTER)

        self.add_button = tk.Button(self.button_frame, text="Add Note", command=self.add_note, bg=button_bg, fg=button_fg)
        self.add_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.delete_button = tk.Button(self.button_frame, text="Delete", command=self.delete_note, bg=button_bg, fg=button_fg)
        self.delete_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.open_button = tk.Button(self.button_frame, text="Open", command=self.open_note, bg=button_bg, fg=button_fg)
        self.open_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.theme_button = tk.Button(self.button_frame, text="Switch Theme", command=self.toggle_theme, bg=button_bg, fg=button_fg)
        self.theme_button.pack(side=tk.LEFT, padx=5, pady=5)

        # Apply the default theme (dark)
        self.theme_manager.apply_theme(root, self.theme_manager.current_theme)

        # Initialize grid view
        self.show_grid_view()

    def show_grid_view(self):
        """
        Display the grid view with note titles.
        """
        bg_color, fg_color, button_bg, button_fg = self.theme_manager.get_theme_colors(self.theme_manager.current_theme)

        # Set correct background color
        self.main_frame.config(bg=bg_color)
        self.button_frame.config(bg=bg_color)

        # Clear the main frame
        for widget in self.main_frame.winfo_children():
            widget.destroy()

        # Fetch notes
        notes = self.get_notes()

        # Display notes in a grid (3 columns)
        for i, note_title in enumerate(notes):
            row = i // 3
            col = i % 3

            note_label = tk.Label(
                self.main_frame,
                text=note_title,
                width=20,
                height=6,
                relief="solid",
                borderwidth=1,
                cursor="hand2",
                wraplength=250,
                bg=button_bg,
                fg=button_fg
            )
            note_label.grid(row=row, column=col, padx=5, pady=5)

            # Bind click event to selection
            note_label.bind("<Button-1>", lambda event, lbl=note_label, title=note_title: self.select_note(lbl, title))

        # Apply theme to existing selected label if any
        if self.selected_label and self.selected_label.winfo_exists():
            self.selected_label.config(bg="lightblue")  # Keep highlight effect

    def show_detail_view(self, title, is_new_note=False):
        """Display the detail view for a specific note."""
        bg_color, fg_color, button_bg, button_fg = self.theme_manager.get_theme_colors(self.theme_manager.current_theme)

        # Set correct background color
        self.main_frame.config(bg=bg_color)
        self.button_frame.config(bg=bg_color)

        # Clear the main frame
        for widget in self.main_frame.winfo_children():
            widget.destroy()

        # Display title
        self.title_entry = tk.Entry(self.main_frame, font=("Arial", 16), bg=button_bg, fg=fg_color)
        self.title_entry.pack(pady=10)
        self.title_entry.insert(0, title if not is_new_note else "")

        # Display content
        self.note_text = tk.Text(self.main_frame, width=50, height=20, bg=button_bg, fg=fg_color)
        self.note_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        if not is_new_note:
            content = self.get_note_content(title)
            self.note_text.insert("1.0", content)

        button_frame = tk.Frame(self.main_frame, bg=bg_color)
        button_frame.pack(anchor=tk.S)

        # Add save button
        save_button = tk.Button(button_frame, text="Save", command=lambda: self.save_note(is_new_note), bg=button_bg, fg=button_fg)
        save_button.pack(side=tk.LEFT, padx=5, pady=5)

        # Add back button
        back_button = tk.Button(button_frame, text="Back", command=self.show_grid_view, bg=button_bg, fg=button_fg)
        back_button.pack(side=tk.LEFT, padx=5, pady=5)

    def add_note(self):
        """Switch to the new note-editing interface."""
        self.show_detail_view("New Note", is_new_note=True)

    def get_notes(self):
        """Fetch notes locally from device storage."""
        # Load local notes from device storage
        try:
            notes_dir = "notes"
            if not os.path.exists(notes_dir):
                os.makedirs(notes_dir)
            return [f[:-4] for f in os.listdir(notes_dir) if f.endswith(".txt")]
        except Exception as e:
            self.show_message(f"Failed to load notes: {e}", title="Error", error=True)
            return []

    def get_note_content(self, title):
        """Fetch note content from local storage."""
        try:
            with open(f"notes/{title}.txt", "r") as file:
                return file.read()
        except FileNotFoundError:
            self.show_message(f"Note '{title}' not found locally.", title="Error", error=True)
            return ""
        except Exception as e:
            self.show_message(f"Failed to load note content: {e}", title="Error", error=True)
            return ""

    def open_note(self, title=None):
        """Open a note in detail view."""
        if not title:
            selected_note = self.get_selected_note()
            if not selected_note:
                self.show_message(f"Please select a note to open.", title="Error", error=True)
                return
            title = selected_note

        self.show_detail_view(title)

    def select_note(self, label, title):
        """
        Highlights the selected note and deselects any previously selected one.
        """
        bg_color, fg_color, button_bg, button_fg = self.theme_manager.get_theme_colors(self.theme_manager.current_theme)

        # Reset the background color of the previously selected label
        if self.selected_label and self.selected_label.winfo_exists():
            self.selected_label.config(bg=button_bg, fg=button_fg)

        # Set new selected label and apply highlight
        self.selected_label = label
        self.selected_note = title
        label.config(bg="lightblue")  # Highlight the selected note


    def get_selected_note(self):
        """Get the currently selected note (for grid view)."""
        # This can be implemented if you add selection logic (e.g., highlighting)
        return self.selected_note

    def save_note(self, is_new_note):
        """Save the current note."""
        title = self.title_entry.get().strip()
        content = self.note_text.get("1.0", tk.END).strip()

        if not title:
            self.show_message(f"Please enter a title for the note.", title="Error", error=True)
            return

        try:
            with open(f"notes/{title}.txt", "w") as file:
                file.write(content)
            self.show_message(f"Note saved successfully!", title="Success", error=False)
            self.show_grid_view()
        except Exception as e:
            self.show_message(f"Failed to save note: {e}", title="Error", error=True)

    def delete_note(self):
        """Delete the selected note locally."""
        selected_note = self.get_selected_note()
        if not selected_note:
            self.show_message(f"Please select a note to delete.", title="Error", error=True)
            return

        # Confirmation dialog using MessagePopup
        confirm = MessagePopup.ask_yes_no(self.root, "Confirm Delete", f"Are you sure you want to delete '{selected_note}'?")
        if confirm:
            try:
                os.remove(f"notes/{selected_note}.txt")
                self.show_message(f"Note '{selected_note}' deleted locally!", title="Success")
                self.show_grid_view()
            except FileNotFoundError:
                self.show_message(f"Note '{selected_note}' not found locally.", title="Error", error=True)
            except Exception as e:
                self.show_message(f"Failed to delete note: {e}", title="Error", error=True)

    def toggle_theme(self):
        """Toggles between light and dark themes and updates the UI."""
        self.theme_manager.toggle_theme(self.root)  # Apply the new theme globally

        # Get new theme colors
        bg_color, fg_color, button_bg, button_fg = self.theme_manager.get_theme_colors(self.theme_manager.current_theme)

        # Apply background color to main_frame
        self.main_frame.config(bg=bg_color)

        # Also update the button_frame (if needed)
        self.button_frame.config(bg=bg_color)

    def show_message(self, message, title="Notification", error=False):
        MessagePopup(self.root, message, title, error)