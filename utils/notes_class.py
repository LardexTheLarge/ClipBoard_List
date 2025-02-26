import os
import tkinter as tk
from tkinter import messagebox, ttk
import requests
from dotenv import load_dotenv
from utils.theme_manager_classes import ThemeManager  # Import the ThemeManager class

class NoteTakerApp:
    def __init__(self, root):
        self.root = root
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

            note_button = tk.Button(
                self.main_frame,
                text=note_title,
                width=20,
                height=5,
                command=lambda title=note_title: self.open_note(title),
                bg=button_bg, fg=button_fg  # Ensure correct theme colors
            )
            note_button.grid(row=row, column=col, padx=5, pady=5)

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
        self.title_entry = tk.Entry(self.main_frame, font=("Arial", 16), bg=bg_color, fg=fg_color)
        self.title_entry.pack(pady=10)
        self.title_entry.insert(0, title if not is_new_note else "")

        # Display content
        self.note_text = tk.Text(self.main_frame, width=50, height=20, bg=bg_color, fg=fg_color)
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

    def get_selected_note(self):
        """Get the currently selected note (for grid view)."""
        # This can be implemented if you add selection logic (e.g., highlighting)
        return None  # Placeholder

    def save_note(self, is_new_note):
        """Save the current note."""
        title = self.title_entry.get().strip()
        content = self.note_text.get("1.0", tk.END).strip()

        if not title:
            messagebox.showwarning("Warning", "Please enter a title for the note.")
            return

        if self.server_available:
            try:
                response = requests.post(
                    f"{self.server_url}/notes",
                    json={"title": title, "content": content},
                )
                if response.status_code == 200:
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
        """Toggles between light and dark themes."""
        self.theme_manager.toggle_theme(self.root)






# import os
# import tkinter as tk
# from tkinter import messagebox, ttk
# import requests
# from dotenv import load_dotenv
# from utils.theme_manager_classes import ThemeManager  # Import the ThemeManager class

# class NoteTakerApp:
#     def __init__(self, root):
#         self.root = root
#         self.root.title("Note Taker")
#         load_dotenv()  # Load environment variables from .env file

#         server_ip = os.getenv("SERVER_IP")
#         self.server_url = f"""http://{server_ip}:5000""" # Replace with your server's IP
#         self.server_available = self.check_server_availability()

#         # Initialize ThemeManager
#         self.theme_manager = ThemeManager()

#         # Create a directory to store notes if it doesn't exist
#         if not os.path.exists("notes"):
#             os.makedirs("notes")

#         # Configure grid weights for responsive layout
#         self.root.grid_columnconfigure(0, weight=1)
#         self.root.grid_columnconfigure(1, weight=1)
#         self.root.grid_columnconfigure(2, weight=1)
#         self.root.grid_columnconfigure(3, weight=1)
#         self.root.grid_rowconfigure(1, weight=1)  # Allow the text area to expand

#         # Dropdown for available notes
#         self.title_entry = ttk.Combobox(root, width=47)
#         self.title_entry.grid(row=0, column=0, padx=10, pady=10, columnspan=4, sticky="ew")  # Span across all columns
#         self.title_entry.bind("<<ComboboxSelected>>", self.load_note_from_dropdown)
#         self.update_note_dropdown()

#         # Note text area
#         self.note_text = tk.Text(root, width=50, height=20)
#         self.note_text.grid(row=1, column=0, padx=10, pady=10, columnspan=4, sticky="nsew")  # Span across all columns

#         # Buttons in one row, responsive to window size
#         self.save_button = tk.Button(root, text="Save Note", command=self.save_note)
#         self.save_button.grid(row=2, column=0, padx=5, pady=10, sticky="ew")

#         self.load_button = tk.Button(root, text="Load Note", command=self.load_note)
#         self.load_button.grid(row=2, column=1, padx=5, pady=10, sticky="ew")

#         self.delete_button = tk.Button(root, text="Delete Note", command=self.delete_note)
#         self.delete_button.grid(row=2, column=2, padx=5, pady=10, sticky="ew")

#         self.theme_button = tk.Button(root, text="Toggle Theme", command=self.toggle_theme)
#         self.theme_button.grid(row=2, column=3, padx=5, pady=10, sticky="ew")

#         # Apply the default theme (dark)
#         self.theme_manager.apply_theme(root, self.theme_manager.current_theme)


#     def check_server_availability(self):
#         """Check if the server is reachable."""
#         try:
#             response = requests.get(f"{self.server_url}/ping", timeout=2)  # Ensure the backend has a `/ping` route
#             return response.status_code == 200
#         except requests.exceptions.RequestException:
#             return False  # If the server is unreachable, switch to offline mode

#     def update_note_dropdown(self):
#         """Update note dropdown from server (if available) or local storage."""
#         if self.server_available:
#             try:
#                 response = requests.get(f"{self.server_url}/notes")
#                 if response.status_code == 200:
#                     self.title_entry["values"] = response.json()
#             except requests.exceptions.RequestException:
#                 self.server_available = False  # If request fails, switch to offline mode

#         if not self.server_available:  # Offline mode: Load local notes
#             local_notes = [f[:-4] for f in os.listdir("notes") if f.endswith(".txt")]
#             self.title_entry["values"] = local_notes

#     def save_note(self):
#         """Save note to server (if available) or locally."""
#         title = self.title_entry.get()
#         content = self.note_text.get("1.0", tk.END).strip()

#         if not title:
#             messagebox.showwarning("Warning", "Please enter a title for the note.")
#             return

#         if self.server_available:
#             try:
#                 response = requests.post(f"{self.server_url}/notes", json={"title": title, "content": content})
#                 if response.status_code == 200:
#                     messagebox.showinfo("Success", "Note saved successfully!")
#                     self.update_note_dropdown()
#                     return
#             except requests.exceptions.RequestException:
#                 self.server_available = False  # Server is down, fallback to offline mode

#         # Save locally if server is unavailable
#         with open(f"notes/{title}.txt", "w") as file:
#             file.write(content)
#         messagebox.showinfo("Success", "Note saved locally!")
#         self.update_note_dropdown()

#     def load_note(self):
#         """Load note from server or local storage."""
#         title = self.title_entry.get()
#         if not title:
#             messagebox.showwarning("Warning", "Please select a note to load.")
#             return

#         if self.server_available:
#             try:
#                 response = requests.get(f"{self.server_url}/notes/{title}")
#                 if response.status_code == 200:
#                     self.note_text.delete("1.0", tk.END)
#                     self.note_text.insert("1.0", response.json()["content"])
#                     return
#             except requests.exceptions.RequestException:
#                 self.server_available = False  # Server is down, switch to offline

#         # Load locally if server is unavailable
#         try:
#             with open(f"notes/{title}.txt", "r") as file:
#                 self.note_text.delete("1.0", tk.END)
#                 self.note_text.insert("1.0", file.read())
#         except FileNotFoundError:
#             messagebox.showwarning("Warning", "Note not found.")

#     def load_note_from_dropdown(self, event=None):
#         """Loads a note when a title is selected from the dropdown."""
#         title = self.title_entry.get()
#         if title:
#             self.load_note_by_title(title)

#     def load_note_by_title(self, title):
#         """Helper method to load a note by title."""
#         try:
#             with open(f"notes/{title}.txt", "r") as file:
#                 content = file.read()
#                 self.note_text.delete("1.0", tk.END)
#                 self.note_text.insert("1.0", content)
#         except FileNotFoundError:
#             messagebox.showwarning("Warning", "Note not found.")

#     def delete_note(self):
#         """Delete note from server or locally."""
#         title = self.title_entry.get()
#         if not title:
#             messagebox.showwarning("Warning", "Please select a note to delete.")
#             return

#         confirm = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete '{title}'?")
#         if not confirm:
#             return

#         if self.server_available:
#             try:
#                 response = requests.delete(f"{self.server_url}/notes/{title}")
#                 if response.status_code == 200:
#                     messagebox.showinfo("Success", f"Note '{title}' deleted successfully!")
#                     self.update_note_dropdown()
#                     return
#             except requests.exceptions.RequestException:
#                 self.server_available = False  # Server is down, switch to offline mode

#         # Delete locally if server is unavailable
#         try:
#             os.remove(f"notes/{title}.txt")
#             messagebox.showinfo("Success", f"Note '{title}' deleted locally!")
#             self.update_note_dropdown()
#         except FileNotFoundError:
#             messagebox.showwarning("Warning", "Note not found locally.")

#     def toggle_theme(self):
#         """Toggles between light and dark themes."""
#         self.theme_manager.toggle_theme(self.root)