import tkinter as tk
from tkinter import ttk


class ThemeManager:
    """
    Manages light and dark themes for Tkinter applications.
    """

    def __init__(self):
        self.current_theme = "dark"  # Default theme

    def apply_theme(self, root, theme):
        """
        Applies the specified theme to the given root window and its child widgets.
        """
        self.current_theme = theme
        bg_color, fg_color, button_bg, button_fg = self.get_theme_colors(theme)

        # Apply theme to root window
        root.config(bg=bg_color)

        # Apply theme to child widgets recursively
        self._apply_theme_to_children(root, bg_color, fg_color, button_bg, button_fg)

    def toggle_theme(self, root):
        """
        Toggles between light and dark themes.
        """
        new_theme = "dark" if self.current_theme == "light" else "light"
        self.apply_theme(root, new_theme)

    def get_theme_colors(self, theme):
        """
        Returns color settings based on the theme.
        """
        if theme == "dark":
            return "darkblue", "white", "darkgray", "black"
        else:
            return "white", "black", "lightgray", "black"

    def _apply_theme_to_children(self, widget, bg_color, fg_color, button_bg, button_fg):
        """
        Recursively applies the theme to child widgets.
        """
        for child in widget.winfo_children():
            # Apply background color universally
            child.config(bg=bg_color)

            # Apply foreground color selectively to text-based widgets
            if isinstance(child, (tk.Label, tk.Button, tk.Checkbutton, tk.Radiobutton)):
                child.config(fg=fg_color)
            elif isinstance(child, tk.Text):
                child.config(fg=fg_color, insertbackground=fg_color)
            elif isinstance(child, ttk.Entry):  # TTK Widgets customization
                style = ttk.Style()
                style.configure("TEntry", fieldbackground=bg_color, foreground=fg_color)

            # Apply button-specific colors
            if isinstance(child, tk.Button):
                child.config(bg=button_bg, fg=button_fg)

            # Recursively apply theme to children
            self._apply_theme_to_children(child, bg_color, fg_color, button_bg, button_fg)

