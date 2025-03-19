import tkinter as tk
from tkinter import Toplevel, Label, Button
from utils.theme_manager_classes import ThemeManager

class MessagePopup:
    def __init__(self, parent, message, title="Notification", error=False):
        self.theme_manager = ThemeManager()
        bg_color, fg_color, button_bg, button_fg = self.theme_manager.get_theme_colors(self.theme_manager.current_theme)

        # Create the popup window
        self.popup = Toplevel(parent)
        self.popup.title(title)
        self.popup.config(bg=bg_color)
        self.popup.geometry("300x150")
        self.popup.resizable(False, False)

        # Create and place the message label
        label = Label(self.popup, text=message, bg=bg_color, fg=fg_color, font=("Helvetica", 12), wraplength=280)
        label.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)

        # Create the close button
        close_button = Button(self.popup, text="OK", command=self.popup.destroy, bg=button_bg, fg=button_fg)
        close_button.pack(pady=10)

        # Center the window
        self.center_window(300, 150)

        # Auto-close for non-error messages after 2 seconds
        if not error:
            parent.after(2000, self.popup.destroy)

    def center_window(self, width, height):
        screen_width = self.popup.winfo_screenwidth()
        screen_height = self.popup.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        self.popup.geometry(f"{width}x{height}+{x}+{y}")

    def ask_yes_no(parent, title, message):
        result = None
        popup = Toplevel(parent)
        theme_manager = ThemeManager()
        bg_color, fg_color, button_bg, button_fg = theme_manager.get_theme_colors(theme_manager.current_theme)

        popup.title(title)
        popup.config(bg=bg_color)
        popup.geometry("300x150")
        popup.resizable(False, False)

        label = Label(popup, text=message, bg=bg_color, fg=fg_color, font=("Helvetica", 12), wraplength=280)
        label.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)

        button_frame = tk.Frame(popup, bg=bg_color)
        button_frame.pack(pady=5)

        def on_yes():
            nonlocal result
            result = True
            popup.destroy()

        def on_no():
            nonlocal result
            result = False
            popup.destroy()

        yes_button = Button(button_frame, text="Yes", command=on_yes, bg=button_bg, fg=button_fg, width=10)
        yes_button.pack(side=tk.LEFT, padx=5)

        no_button = Button(button_frame, text="No", command=on_no, bg=button_bg, fg=button_fg, width=10)
        no_button.pack(side=tk.RIGHT, padx=5)

        # Center window
        screen_width = popup.winfo_screenwidth()
        screen_height = popup.winfo_screenheight()
        x = (screen_width // 2) - (300 // 2)
        y = (screen_height // 2) - (150 // 2)
        popup.geometry(f"300x150+{x}+{y}")

        popup.wait_window()  # Pause execution until the popup is closed
        return result

