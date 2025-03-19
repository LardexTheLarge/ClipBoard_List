import pyperclip
import time
import threading
import tkinter as tk
from tkinter import messagebox, Toplevel, Text, ttk
from utils.theme_manager_classes import ThemeManager  # Import the ThemeManager class
from utils.message_popup import MessagePopup
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

        self.theme_manager = ThemeManager()  # Initialize the theme manager
        bg_color, fg_color, button_bg, button_fg = self.theme_manager.get_theme_colors(self.theme_manager.current_theme)

        self.selected_label = None  # To keep track of the currently selected label
        self.is_editor_mode = False  # Track whether the app is in editor mode

        # Create and pack the frame that will hold the grid of clipboard items
        self.grid_frame = tk.Frame(root)
        self.grid_frame.pack(fill=tk.BOTH, expand=True)

        # Create a frame to hold the buttons horizontally
        self.button_frame = tk.Frame(root, bg=bg_color)
        self.button_frame.pack(side=tk.BOTTOM, pady=10, anchor=tk.CENTER)

        # Create and pack buttons for refresh, edit, and delete actions
        self.refresh_button = tk.Button(self.button_frame, text="Refresh", command=self.refresh_grid, bg=button_bg, fg=button_fg)
        self.refresh_button.pack(side=tk.LEFT, padx=5)

        self.edit_button = tk.Button(self.button_frame, text="Edit", command=self.toggle_editor_mode, bg=button_bg, fg=button_fg)
        self.edit_button.pack(side=tk.LEFT, padx=5)

        self.delete_button = tk.Button(self.button_frame, text="Delete", command=self.delete_selected, bg=button_bg, fg=button_fg)
        self.delete_button.pack(side=tk.LEFT, padx=5)
    
        self.theme_toggle_button = tk.Button(self.button_frame, text="Switch Theme", command=self.toggle_theme, bg=button_bg, fg=button_fg)
        self.theme_toggle_button.pack(side=tk.LEFT, padx=5)

        # Apply the default system theme
        self.apply_theme()

        self.refresh_grid()  # Initial refresh to display the current clipboard history

    def toggle_theme(self):
        """
        Toggles between light and dark themes.
        """
        # Toggle the theme using ThemeManager
        self.theme_manager.toggle_theme(self.root)

        # Reapply the theme to all widgets
        self.apply_theme()

    def apply_theme(self):
        """
        Applies the current theme to all widgets in the app.
        """
        # Get the current theme colors
        bg_color, fg_color, button_bg, button_fg = self.theme_manager.get_theme_colors(self.theme_manager.current_theme)
        
        # Apply theme to the root window
        self.root.config(bg=bg_color)

        # Apply theme to all frames
        self.grid_frame.config(bg=bg_color)
        self.button_frame.config(bg=bg_color)

        # Apply theme to all buttons
        for widget in self.button_frame.winfo_children():
            if isinstance(widget, tk.Button):
                widget.config(bg=button_bg, fg=button_fg)

        # Apply theme to all labels in the grid
        for widget in self.grid_frame.winfo_children():
            if isinstance(widget, tk.Label):
                widget.config(bg=button_bg, fg=button_fg)

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
        bg_color, fg_color, button_bg, button_fg = self.theme_manager.get_theme_colors(self.theme_manager.current_theme)

        for widget in self.grid_frame.winfo_children():
            widget.destroy()  # Clear existing widgets
        
        clipboard_history = self.clipboard_manager.get_history()
        num_columns = 3  # Number of columns in the grid
        fixed_width = 30  # Fixed width for labels
        max_length = 20  # Maximum length for truncation

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
                bg=button_bg,
                fg=button_fg
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
        MessagePopup(self.root, message, title, error)


    def select_label(self, label):
        """
        Highlights the selected label and deselects any previously selected label.
        """
        bg_color, fg_color, button_bg, button_fg = self.theme_manager.get_theme_colors(self.theme_manager.current_theme)
        if self.selected_label:
            if self.selected_label.winfo_exists():
                self.selected_label.config(bg=button_bg)
        self.selected_label = label
        label.config(bg="lightblue")

    def delete_selected(self):
        """
        Deletes the currently selected label's text from history and refreshes the grid.
        """
        if self.selected_label:
            if self.is_editor_mode:
                item_to_delete = self.selected_label.full_text  # Get the full text from the label
                # Confirmation dialog using MessagePopup
                confirm = MessagePopup.ask_yes_no(self.root, "Confirm Delete", "Are you sure you want to delete item?")
                if confirm:
                    self.clipboard_manager.clipboard_history.remove(item_to_delete)  # Remove item from history
                    self.clipboard_manager.save_history()  # Save updated history to file
                    self.refresh_grid()  # Refresh the grid to reflect changes
                    self.selected_label = None  # Reset the selected label
                    self.show_message("Item Deleted", title="Success")
                    self.switch_to_grid_mode()
                else:
                    self.show_message("Deletion Canceled", title="Success")
            else:
                self.show_message("No item selected!", title="Error", error=True)

    def toggle_editor_mode(self):
        """
        Toggles between grid mode and editor mode.
        """
        if not self.selected_label:
            self.show_message("No item selected!", title="Error", error=True)
            return
        
        if self.is_editor_mode:
            # Switch back to grid mode
            self.switch_to_grid_mode()
        else:
            # Switch to editor mode
            self.switch_to_editor_mode()

    def switch_to_editor_mode(self):
        """
        Switches the main window to editor mode.
        """
        bg_color, fg_color, button_bg, button_fg = self.theme_manager.get_theme_colors(self.theme_manager.current_theme)
        if not self.selected_label:
            self.show_message("No item selected!", title="Error", error=True)
            return

        # Hide the grid frame
        self.grid_frame.pack_forget()

        # Create the editor frame
        self.editor_frame = tk.Frame(self.root)
        self.editor_frame.pack(fill=tk.BOTH, expand=True)
        self.editor_frame.config(bg=bg_color)

        # Get the selected note's text
        old_text = self.selected_label.full_text

        # Create a text widget for editing
        self.text_area = tk.Text(self.editor_frame, width=60, height=20)
        self.text_area.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.text_area.config(bg=button_bg)
        self.text_area.insert(tk.END, old_text)

        # Create a frame for editor buttons
        editor_button_frame = tk.Frame(self.editor_frame)
        editor_button_frame.pack(side=tk.BOTTOM)
        editor_button_frame.config(bg=bg_color)

        # Create Save button
        save_button = tk.Button(editor_button_frame, text="Save", command=self.save_edited_text)
        save_button.pack(side=tk.LEFT, padx=5)
        save_button.config(bg=button_bg)

        # Create Cancel button
        cancel_button = tk.Button(editor_button_frame, text="Cancel", command=self.switch_to_grid_mode)
        cancel_button.pack(side=tk.LEFT, padx=5)
        cancel_button.config(bg=button_bg)

        # Update the mode flag
        self.is_editor_mode = True

    def switch_to_grid_mode(self):
        """
        Switches the main window back to grid mode.
        """
        # Hide the editor frame
        self.editor_frame.pack_forget()

        # Show the grid frame
        self.grid_frame.pack(fill=tk.BOTH, expand=True)

        # Update the mode flag
        self.is_editor_mode = False

    def save_edited_text(self):
        """
        Saves the edited text, updates history, and refreshes the grid.
        """
        if not self.selected_label:
            self.show_message("No item selected!", title="Error", error=True)
            return
        
        new_text = self.text_area.get("1.0", tk.END).strip()
        if new_text:
            # Update the clipboard history with the new text
            old_text = self.selected_label.full_text
            self.clipboard_manager.clipboard_history[self.clipboard_manager.clipboard_history.index(old_text)] = new_text
            self.clipboard_manager.save_history()

            # Refresh the grid to reflect changes
            self.refresh_grid()

            # Switch back to grid mode
            self.switch_to_grid_mode()


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
