import tkinter as tk
from tkinter import ttk
import threading
from utils.clipboard_classes import ClipboardManager, ClipboardApp
from utils.theme_manager_classes import ThemeManager


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
        self.root.geometry("400x300")

        # Add a toggle theme button
        theme_button = tk.Button(root, text="Switch Theme", command=self.toggle_theme)
        theme_button.pack(pady=5)
        
        # Title label
        title_label = tk.Label(root, text="App Launcher", font=("Helvetica", 16, "bold"))
        title_label.pack(pady=10)

        # App list frame
        self.app_list_frame = tk.Frame(root)
        self.app_list_frame.pack(pady=10, fill=tk.BOTH, expand=True)

        # Scrollable listbox
        self.app_listbox = tk.Listbox(self.app_list_frame, height=10, width=30)
        self.app_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Scrollbar
        scrollbar = tk.Scrollbar(self.app_list_frame, orient=tk.VERTICAL)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.app_listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.app_listbox.yview)

        # Action buttons
        btn_frame = tk.Frame(root)
        btn_frame.pack(pady=10)

        self.launch_button = tk.Button(btn_frame, text="Launch App", command=self.launch_selected_app)
        self.launch_button.pack(side=tk.LEFT, padx=5)

        self.add_app_button = tk.Button(btn_frame, text="Add App", command=self.add_new_app)
        self.add_app_button.pack(side=tk.LEFT, padx=5)

        self.theme_manager.apply_theme(self.root, "dark")  # Default to light theme

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
        # Example: Adding Clipboard App
        self.add_app("Clipboard Manager", self.launch_clipboard_app)

    def add_app(self, app_name, launch_function):
        """
        Adds a new app to the launcher.
        """
        self.apps[app_name] = launch_function
        self.app_listbox.insert(tk.END, app_name)

    def launch_selected_app(self):
        """
        Launches the selected application from the list.
        """
        selected_index = self.app_listbox.curselection()
        if selected_index:
            app_name = self.app_listbox.get(selected_index)
            if app_name in self.apps:
                self.apps[app_name]()  # Call the launch function
            else:
                self.show_message(f"App '{app_name}' not found!", error=True)
        else:
            self.show_message("No app selected!", error=True)

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

    def show_message(self, message, error=False):
        """
        Displays a message to the user.
        """
        msg_type = "Error" if error else "Info"
        tk.messagebox.showinfo(msg_type, message)