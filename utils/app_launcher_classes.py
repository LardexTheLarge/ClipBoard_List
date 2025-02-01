import tkinter as tk
from tkinter import ttk
import threading
from utils.clipboard_classes import ClipboardManager, ClipboardApp
from utils.theme_manager_classes import ThemeManager
from utils.notes_class import NoteTakerApp


class AppLauncher:
    """
    A launcher interface to manage and open multiple applications.
    """

    def __init__(self, root):
        """
        Initializes the App Launcher with a list of applications.
        """
        self.root = root
        self.root.title("Application Launcher")
        self.theme_manager = ThemeManager()
        self.root.geometry("300x100")

        # Configure grid weights for responsive layout
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_rowconfigure(1, weight=1)  # Allow the dropdown to expand

        # Dropdown for app selection
        self.app_dropdown = ttk.Combobox(root, width=30)
        self.app_dropdown.grid(row=0, column=0, padx=10, pady=10, columnspan=2, sticky="ew")
        self.app_dropdown.bind("<<ComboboxSelected>>", self.launch_selected_app)

        # Buttons in one row, responsive to window size
        self.launch_button = tk.Button(root, text="Launch App", command=self.launch_selected_app)
        self.launch_button.grid(row=1, column=0, padx=5, pady=10, sticky="ew")

        self.theme_button = tk.Button(root, text="Switch Theme", command=self.toggle_theme)
        self.theme_button.grid(row=1, column=1, padx=5, pady=10, sticky="ew")

        # Apply the default theme (dark)
        self.theme_manager.apply_theme(root, self.theme_manager.current_theme)

        # Dictionary to store available apps and their launch functions
        self.apps = {}
        self.populate_apps()
    
    def toggle_theme(self):
        """
        Toggles between light and dark themes using ThemeManager.
        """
        self.theme_manager.toggle_theme(self.root)

    def populate_apps(self):
        """
        Populates the list of apps in the launcher.
        """
        
        self.add_app("Clipboard Manager", self.launch_clipboard_app)
        self.add_app("Note Taker", self.launch_notetaker_app)

    def add_app(self, app_name, launch_function):
        """
        Adds a new app to the launcher.
        """
        self.apps[app_name] = launch_function
        self.app_dropdown["values"] = list(self.apps.keys())  # Update dropdown values

    def launch_selected_app(self, event=None):
        """
        Launches the selected application from the dropdown.
        """
        app_name = self.app_dropdown.get()

        if app_name in self.apps:
            self.apps[app_name]()  # Call the launch function
        else:
            self.show_message(f"App '{app_name}' not found!", error=True)

    def add_new_app(self):
        """
        Adds a new app through a dialog (to be implemented if required).
        """
        self.show_message("Feature to add new apps dynamically is coming soon!", error=False)

    def launch_clipboard_app(self):
        """
        Launches the Clipboard Manager application.
        """
        new_window = tk.Toplevel(self.root)
        clipboard_manager = ClipboardManager()
        # Run the clipboard monitoring in a separate thread
        monitor_thread = threading.Thread(target=clipboard_manager.monitor_clipboard)
        monitor_thread.daemon = True
        monitor_thread.start()
        ClipboardApp(new_window, clipboard_manager)

    def launch_notetaker_app(self):
        """
        Launches the Note taking application.
        """
        new_window = tk.Toplevel(self.root)
        NoteTakerApp(new_window)

    def show_message(self, message, error=False):
        """
        Displays a message to the user.
        """
        msg_type = "Error" if error else "Info"
        tk.messagebox.showinfo(msg_type, message)