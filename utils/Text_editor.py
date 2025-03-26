import tkinter as tk
from tkinter import filedialog, messagebox, font
from tkinter.scrolledtext import ScrolledText
from utils.theme_manager_classes import ThemeManager
from utils.message_popup import MessagePopup

class TextEditorApp:
    def __init__(self, root):
        """Initialize the text editor application."""
        self.root = root
        self.root.title("Text Editor")
        self.root.minsize(800, 600)

        # Initialize Theme Manager
        self.theme_manager = ThemeManager()
        bg_color, fg_color, button_bg, button_fg = self.theme_manager.get_theme_colors(self.theme_manager.current_theme)

        # Text area with scrollbars
        self.text_area = ScrolledText(root, wrap="word", undo=True, bg=bg_color, fg=fg_color)
        self.text_area.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Track the current font for new text
        self.current_font = ("Arial", 12)
        self.text_area.configure(font=self.current_font)

        # Create a tag for the current font
        self.text_area.tag_configure("current_font", font=self.current_font)

        # Bind key press to apply the current font to new text
        self.text_area.bind("<KeyPress>", self.apply_current_font)

        # Create menu bar
        self.create_menu()

        # Apply theme
        self.theme_manager.apply_theme(root, self.theme_manager.current_theme)

    def create_menu(self):
        """Create the menu bar with file and edit options."""
        menu_bar = tk.Menu(self.root)

        # File menu
        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="New", command=self.new_file)
        file_menu.add_command(label="Open", command=self.open_file)
        file_menu.add_command(label="Save", command=self.save_file)
        file_menu.add_command(label="Save As", command=self.save_file_as)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        menu_bar.add_cascade(label="File", menu=file_menu)

        # Edit menu
        edit_menu = tk.Menu(menu_bar, tearoff=0)
        edit_menu.add_command(label="Undo", command=self.text_area.edit_undo)
        edit_menu.add_command(label="Redo", command=self.text_area.edit_redo)
        edit_menu.add_separator()
        edit_menu.add_command(label="Cut", command=lambda: self.text_area.event_generate("<<Cut>>"))
        edit_menu.add_command(label="Copy", command=lambda: self.text_area.event_generate("<<Copy>>"))
        edit_menu.add_command(label="Paste", command=lambda: self.text_area.event_generate("<<Paste>>"))
        edit_menu.add_command(label="Select All", command=lambda: self.text_area.event_generate("<<SelectAll>>"))
        menu_bar.add_cascade(label="Edit", menu=edit_menu)

        # Text menu
        text_menu = tk.Menu(menu_bar, tearoff=0)
        
        # Font submenu
        font_submenu = tk.Menu(text_menu, tearoff=0)
        font_choices = ["Arial", "Times New Roman", "Courier New", "Verdana", "Comic Sans MS"]
        for font_choice in font_choices:
            font_submenu.add_command(label=font_choice, command=lambda f=font_choice: self.change_font(f))
        
        # Add the font submenu to the text menu
        text_menu.add_cascade(label="Change Font", menu=font_submenu)
        
        menu_bar.add_cascade(label="Text", menu=text_menu)

        self.root.config(menu=menu_bar)

    def new_file(self):
        """Clears the text area to start a new file."""
        self.text_area.delete(1.0, tk.END)

    def open_file(self):
        """Opens a text file and loads it into the text area."""
        file_path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])
        if file_path:
            with open(file_path, "r") as file:
                self.text_area.delete(1.0, tk.END)
                self.text_area.insert(tk.END, file.read())
                # Apply current font to all new text after loading
                self.text_area.tag_add("current_font", "1.0", "end")

    def save_file(self):
        """Saves the current content to a file."""
        file_path = filedialog.asksaveasfilename(defaultextension=".txt",
                                                filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])
        if file_path:
            with open(file_path, "w") as file:
                file.write(self.text_area.get(1.0, tk.END))

    def save_file_as(self):
        """Saves the content to a new file."""
        self.save_file()

    def change_font(self, font_name):
        """Change the font for new text only."""
        current_font_size = font.Font(font=self.text_area['font']).actual()['size']
        self.current_font = (font_name, current_font_size)

        # Generate a unique tag for the new font
        font_tag = f"font_{font_name}_{current_font_size}"
        
        # Define the tag with the selected font
        self.text_area.tag_configure(font_tag, font=self.current_font)

        # Apply this tag to all new text
        self.text_area.bind("<Key>", lambda event: self.apply_current_font(font_tag))

    def apply_current_font(self, font_tag):
        """Apply the selected font tag to new text only."""
        self.text_area.tag_add(font_tag, "insert-1c", "insert")
