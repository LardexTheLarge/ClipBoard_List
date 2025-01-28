import pyperclip
import time
import threading
import tkinter as tk
from tkinter import messagebox, Toplevel, Text, ttk
import json
import os

class ClipboardManager:
    """
    Manages clipboard history and interacts with clipboard.
    """

    def __init__(self, clipboard_app=None):
        """
        Initializes the ClipboardManager with optional reference to ClipboardApp.
        """
        self.clipboard_history = []
        self.history_file = "clipboard_history.json"
        self.clipboard_app = clipboard_app  # Reference to the ClipboardApp instance
        self.load_history()  # Load existing history from file

    def monitor_clipboard(self):
        """
        Continuously monitors the clipboard for new text and updates history.
        Runs in a separate thread.
        """
        previous_text = ""
        while True:
            current_text = pyperclip.paste()  # Get current text from clipboard
            if current_text != previous_text and current_text not in self.clipboard_history:
                self.add_to_history(current_text)  # Add new text to history
                self.save_history()  # Save updated history to file
                previous_text = current_text
                if self.clipboard_app:
                    self.clipboard_app.refresh_grid()  # Refresh the grid in the app
            time.sleep(1)  # Check clipboard every second

    def add_to_history(self, text):
        """
        Adds new text to clipboard history and removes oldest item if history exceeds 30 items.
        """
        if len(self.clipboard_history) >= 30:
            self.clipboard_history.pop(0)  # Remove the oldest item
        self.clipboard_history.append(text)

    def get_history(self):
        """
        Returns the current clipboard history.
        """
        return self.clipboard_history

    def save_history(self):
        """
        Saves the clipboard history to a JSON file.
        """
        with open(self.history_file, 'w') as f:
            json.dump(self.clipboard_history, f)

    def load_history(self):
        """
        Loads clipboard history from a JSON file if it exists.
        """
        if os.path.exists(self.history_file):
            with open(self.history_file, 'r') as f:
                self.clipboard_history = json.load(f)

class ClipboardApp:
    """
    The GUI application for managing and displaying clipboard history.
    """

    def __init__(self, root, clipboard_manager):
        """
        Initializes the ClipboardApp with the main application window and clipboard manager.
        """
        self.root = root
        self.root.title("Clipboard Manager")
        self.clipboard_manager = clipboard_manager
        self.clipboard_manager.clipboard_app = self  # Pass reference to ClipboardManager
        # self.theme_manager = ThemeManager()  # Initialize the theme manager


        self.selected_label = None  # To keep track of the currently selected label
        self.current_theme = "dark"  # Default theme

        # Create and pack the frame that will hold the grid of clipboard items
        self.grid_frame = tk.Frame(root)
        self.grid_frame.pack(pady=20)

        # Create a frame to hold the buttons horizontally
        self.button_frame = tk.Frame(root)
        self.button_frame.pack(pady=10)

        # Create and pack buttons for refresh, edit, and delete actions
        self.refresh_button = tk.Button(self.button_frame, text="Refresh", command=self.refresh_grid)
        self.refresh_button.pack(side=tk.LEFT, padx=5)

        self.edit_button = tk.Button(self.button_frame, text="Edit", command=self.edit_selected)
        self.edit_button.pack(side=tk.LEFT, padx=5)

        self.delete_button = tk.Button(self.button_frame, text="Delete", command=self.delete_selected)
        self.delete_button.pack(side=tk.LEFT, padx=5)
    
        self.theme_toggle_button = tk.Button(self.button_frame, text="Switch to Dark Theme", command=self.toggle_theme)
        self.theme_toggle_button.pack(side=tk.LEFT, padx=5)

        self.refresh_grid()  # Initial refresh to display the current clipboard history
        
        # Apply the default system theme
        self.apply_system_theme(self.current_theme)

    def apply_system_theme(self, theme):
        """
        Configures the application to use the specified theme (light/dark).
        """
        try:
            # Use ttk style for modern theming
            style = ttk.Style()

            # Apply the specified theme
            if theme == "dark":
                self.root.config(bg="darkblue")
                self.grid_frame.config(bg="darkblue")
                self.button_frame.config(bg="darkblue")
                self.refresh_button.config(bg="darkgray", fg="black")
                self.edit_button.config(bg="darkgray", fg="black")
                self.delete_button.config(bg="darkgray", fg="black")
                self.theme_toggle_button.config(bg="darkgray", fg="black", text="Switch to Light Theme")
                # Update grid items for dark mode
                for widget in self.grid_frame.winfo_children():
                    widget.config(bg="darkgray", fg="black")
            else:  # Light theme
                self.root.config(bg="white")
                self.grid_frame.config(bg="white")
                self.button_frame.config(bg="white")
                self.refresh_button.config(bg="lightgray", fg="black")
                self.edit_button.config(bg="lightgray", fg="black")
                self.delete_button.config(bg="lightgray", fg="black")
                self.theme_toggle_button.config(bg="lightgray", fg="black", text="Switch to Dark Theme")
                # Update grid items for light mode
                for widget in self.grid_frame.winfo_children():
                    widget.config(bg="white", fg="black")

        except Exception as e:
            print(f"Error applying theme: {e}")

    def toggle_theme(self):
        """
        Toggles between light and dark themes.
        """
        self.current_theme = "dark" if self.current_theme == "light" else "light"
        self.apply_system_theme(self.current_theme)

    def truncate_text(self, text, max_length=20):
        """
        Truncates the text to a specified maximum length, adding ellipsis if truncated.
        """
        return (text[:max_length] + '...') if len(text) > max_length else text

    def calculate_label_height(self, text, max_length=20):
        """
        Calculates the height of the label based on the length of the truncated text.
        """
        lines = (len(text) // max_length) + 1
        return lines * 2  # Adjust multiplier as needed to fit text properly
    
    def center_window(self, window, width, height):
        """
        Centers a window on the screen.
        """
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        window.geometry(f"{width}x{height}+{x}+{y}")

    def refresh_grid(self):
        """
        Refreshes the grid to display the current clipboard history.
        """
        for widget in self.grid_frame.winfo_children():
            widget.destroy()  # Clear existing widgets
        
        clipboard_history = self.clipboard_manager.get_history()
        num_columns = 3  # Number of columns in the grid
        fixed_width = 30  # Fixed width for labels
        max_length = 20  # Maximum length for truncation

        # Configure theme-based appearance
        bg_color = "darkgray" if self.current_theme == "dark" else "white"
        fg_color = "black" if self.current_theme == "dark" else "black"

        for index, item in enumerate(clipboard_history):
            row = index // num_columns
            column = index % num_columns
            truncated_text = self.truncate_text(item, max_length)  # Truncate text for label
            label_height = self.calculate_label_height(truncated_text, max_length)  # Calculate label height

            # Create a label for each item in the history
            label = tk.Label(
                self.grid_frame,
                text=truncated_text,
                borderwidth=1,
                relief="solid",
                width=fixed_width,
                height=label_height,
                wraplength=250,
                anchor=tk.W,
                justify=tk.LEFT,
                bg=bg_color,
                fg=fg_color
            )
            label.grid(row=row, column=column, padx=5, pady=5)
            label.full_text = item  # Store the full text in the label

            # Bind double-click to copy text and single-click to select label
            label.bind("<Double-Button-1>", lambda event, text=item: self.copy_text(text))
            label.bind("<Button-1>", lambda event, lbl=label: self.select_label(lbl))

        # Configure the grid to expand with window size
        for column in range(num_columns):
            self.grid_frame.columnconfigure(column, weight=1)
        for row in range((len(clipboard_history) + num_columns - 1) // num_columns):
            self.grid_frame.rowconfigure(row, weight=1)

    def show_message(self, message, title="Notification", error=False):
        """
        Displays a themed messagebox-style popup with the current theme applied.
        """
        # Create a Toplevel window
        messagebox = Toplevel(self.root)
        messagebox.title(title)

        # Configure theme-based appearance
        bg_color = "darkred" if error else ("darkblue" if self.current_theme == "dark" else "white")
        fg_color = "white" if self.current_theme == "dark" or error else "black"

        # Apply theme settings to the Toplevel window
        messagebox.config(bg=bg_color)
        messagebox.geometry("300x150")  # Customize size as needed
        messagebox.resizable(False, False)

        # Add a label for the message
        label = tk.Label(messagebox, text=message, bg=bg_color, fg=fg_color, font=("Helvetica", 12), wraplength=280)
        label.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)

        # Add a Close button
        close_button = tk.Button(
            messagebox,
            text="OK",
            command=messagebox.destroy,
            bg="darkgray" if self.current_theme == "dark" else "lightgray",
            fg="black" if self.current_theme == "dark" else "black",
        )
        close_button.pack(pady=10)

        # Center the popup on the screen
        self.center_window(messagebox, 300, 150)

        # Auto-close successful notifications after 2 seconds
        if not error:
            self.root.after(2000, messagebox.destroy)


    def select_label(self, label):
        """
        Highlights the selected label and deselects any previously selected label.
        """
        bg_color = "darkgray" if self.current_theme == "dark" else "white"
        if self.selected_label:
            if self.selected_label.winfo_exists():
                self.selected_label.config(bg=bg_color)
        self.selected_label = label
        label.config(bg="lightblue")

    def delete_selected(self):
        """
        Deletes the currently selected label's text from history and refreshes the grid.
        """
        if self.selected_label:
            item_to_delete = self.selected_label.full_text  # Get the full text from the label
            self.clipboard_manager.clipboard_history.remove(item_to_delete)  # Remove item from history
            self.clipboard_manager.save_history()  # Save updated history to file
            self.refresh_grid()  # Refresh the grid to reflect changes
            self.selected_label = None
        else:
            self.show_message("No item selected!", title="Error", error=True)

    def edit_selected(self):
        """
        Opens a new window for editing the text of the currently selected label.
        """
        if self.selected_label:
            old_text = self.selected_label.full_text  # Get the full text from the label
            edit_window = Toplevel(self.root)  # Create a new top-level window
            edit_window.title("Edit Text")

            # Configure theme-based appearance
            bg_color = "darkblue" if self.current_theme == "dark" else "white"
            fg_color = "white" if self.current_theme == "dark" else "black"
            btn_bg_color = "darkgray" if self.current_theme == "dark" else "lightgray"
            btn_fg_color = "black" if self.current_theme == "dark" else "black"

            edit_window.config(bg=bg_color)

            # Create a text widget with specified dimensions for editing
            text_area = Text(edit_window, width=60, height=20, bg=bg_color, fg=fg_color, insertbackground=fg_color)
            text_area.pack(padx=10, pady=10)
            text_area.insert(tk.END, old_text)  # Insert the old text into the text widget

            # Create a save button to save changes
            save_button = tk.Button(
                edit_window,
                text="Save",
                command=lambda: self.save_edited_text(edit_window, text_area, old_text),
                bg=btn_bg_color,
                fg=btn_fg_color
            )
            save_button.pack(pady=10)

            # Center the window
            self.center_window(edit_window, 500, 400)
        else:
            self.show_message("No item selected!", title="Error", error=True)


    def save_edited_text(self, window, text_area, old_text):
        """
        Saves the edited text, updates history, and refreshes the grid.
        """
        new_text = text_area.get("1.0", tk.END).strip()  # Get the new text from the text widget
        if new_text:
            # Update the clipboard history with the new text
            self.clipboard_manager.clipboard_history[self.clipboard_manager.clipboard_history.index(old_text)] = new_text
            self.clipboard_manager.save_history()  # Save updated history to file
            self.refresh_grid()  # Refresh the grid to reflect changes
            self.selected_label = None
            window.destroy()  # Close the edit window
            self.show_message("Text edited successfully!", title="Success")
        else:
            self.show_message("Text cannot be empty!", title="Error", error=True)

    def copy_text(self, text):
        """
        Copies the specified text to the clipboard and shows a themed message.
        """
        if text:
            pyperclip.copy(text)
            self.show_message("Text copied to clipboard!", title="Success")
        else:
            self.show_message("No text selected!", title="Error", error=True)
