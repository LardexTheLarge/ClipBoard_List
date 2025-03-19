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
        MessagePopup.center_window(self.popup, 300, 150)

        # Auto-close for non-error messages after 2 seconds
        if not error:
            parent.after(2000, self.popup.destroy)

    @staticmethod
    def center_window(window, width, height):
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        window.geometry(f"{width}x{height}+{x}+{y}")

    @staticmethod
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

        # Center the window
        MessagePopup.center_window(popup, 300, 150)

        popup.wait_window()  # Pause execution until the popup is closed
        return result

