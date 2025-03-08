import os
import tkinter as tk
from tkinter import messagebox, ttk
import requests
from dotenv import load_dotenv
from utils.theme_manager_classes import ThemeManager  # Import the ThemeManager class

class NoteTakerApp:
    def __init__(self, root):
        self.root = root
        self.selected_label = None  # Track the currently selected note
        self.selected_note = None  # Track selected note title
        self.root.title("Note Taker")
        load_dotenv()

        server_ip = os.getenv("SERVER_IP")
        self.server_url = f"http://{server_ip}:5000"
        self.server_available = self.check_server_availability()

        # Initialize ThemeManager
        self.theme_manager = ThemeManager()
        bg_color, fg_color, button_bg, button_fg = self.theme_manager.get_theme_colors(self.theme_manager.current_theme)

        # Apply dark blue background
        self.root.config(bg=bg_color)

        # Ensure there's only ONE main frame with the correct theme
        self.main_frame = tk.Frame(root, bg=bg_color)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Buttons frame
        self.button_frame = tk.Frame(root, bg=bg_color)
        self.button_frame.pack(side=tk.BOTTOM, fill=tk.X)

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


    def check_server_availability(self):
        """Check if the server is reachable."""
        try:
            response = requests.get(f"{self.server_url}/ping", timeout=2)  # Ensure the backend has a `/ping` route
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False  # If the server is unreachable, switch to offline mode

    def show_grid_view(self):
        """Display the grid view with note titles."""
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
                bg=button_bg,  # Apply theme background
                fg=button_fg   # Apply theme text color
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

        # Add save button
        save_button = tk.Button(self.main_frame, text="Save", command=lambda: self.save_note(is_new_note), bg=button_bg, fg=button_fg)
        save_button.pack(side=tk.LEFT, padx=5, pady=5)

        # Add back button
        back_button = tk.Button(self.main_frame, text="Back", command=self.show_grid_view, bg=button_bg, fg=button_fg)
        back_button.pack(side=tk.LEFT, padx=5, pady=5)

    def add_note(self):
        """Switch to the new note-editing interface."""
        self.show_detail_view("New Note", is_new_note=True)

    def get_notes(self):
        """Fetch notes from server or local storage."""
        if self.server_available:
            try:
                response = requests.get(f"{self.server_url}/notes")
                if response.status_code == 200:
                    return response.json()
            except requests.exceptions.RequestException:
                self.server_available = False  # Server is down, switch to offline mode

        # Offline mode: Load local notes
        return [f[:-4] for f in os.listdir("notes") if f.endswith(".txt")]

    def get_note_content(self, title):
        """Fetch note content from server or local storage."""
        if self.server_available:
            try:
                response = requests.get(f"{self.server_url}/notes/{title}")
                if response.status_code == 200:
                    return response.json()["content"]
            except requests.exceptions.RequestException:
                self.server_available = False  # Server is down, switch to offline mode

        # Offline mode: Load local note
        try:
            with open(f"notes/{title}.txt", "r") as file:
                return file.read()
        except FileNotFoundError:
            return "Note not found."

    def open_note(self, title=None):
        """Open a note in detail view."""
        if not title:
            selected_note = self.get_selected_note()
            if not selected_note:
                messagebox.showwarning("Warning", "Please select a note to open.")
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
            messagebox.showwarning("Warning", "Please enter a title for the note.")
            return

        if self.server_available:
            try:
                response = requests.put(
                    f"{self.server_url}/notes/{title}",
                    json={"title": title, "content": content},
                )
                if response.status_code in [200, 201]:
                    messagebox.showinfo("Success", "Note saved successfully!")
                    self.show_grid_view()
                    return
            except requests.exceptions.RequestException:
                self.server_available = False  # Server is down, switch to offline mode

        # Save locally if server is unavailable
        with open(f"notes/{title}.txt", "w") as file:
            file.write(content)
        messagebox.showinfo("Success", "Note saved locally!")
        self.show_grid_view()

    def delete_note(self):
        """Delete the selected note."""
        selected_note = self.get_selected_note()
        if not selected_note:
            messagebox.showwarning("Warning", "Please select a note to delete.")
            return

        confirm = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete '{selected_note}'?")
        if not confirm:
            return

        if self.server_available:
            try:
                response = requests.delete(f"{self.server_url}/notes/{selected_note}")
                if response.status_code == 200:
                    messagebox.showinfo("Success", f"Note '{selected_note}' deleted successfully!")
                    self.show_grid_view()
                    return
            except requests.exceptions.RequestException:
                self.server_available = False  # Server is down, switch to offline mode

        # Delete locally if server is unavailable
        try:
            os.remove(f"notes/{selected_note}.txt")
            messagebox.showinfo("Success", f"Note '{selected_note}' deleted locally!")
            self.show_grid_view()
        except FileNotFoundError:
            messagebox.showwarning("Warning", "Note not found locally.")

    def toggle_theme(self):
        """Toggles between light and dark themes and updates the UI."""
        self.theme_manager.toggle_theme(self.root)  # Apply the new theme globally

        # Get new theme colors
        bg_color, fg_color, button_bg, button_fg = self.theme_manager.get_theme_colors(self.theme_manager.current_theme)

        # Apply background color to main_frame
        self.main_frame.config(bg=bg_color)

        # Also update the button_frame (if needed)
        self.button_frame.config(bg=bg_color)