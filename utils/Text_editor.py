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
        self.root.minsize(845, 600)

        # Initialize Theme Manager
        self.theme_manager = ThemeManager()
        bg_color, fg_color, button_bg, button_fg = self.theme_manager.get_theme_colors(self.theme_manager.current_theme)

        # Create a container frame for the text area with fixed size
        self.text_frame = tk.Frame(root, bg=bg_color)
        self.text_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Text area with scrollbars - fixed size (adjust width and height as needed)
        self.text_area = ScrolledText(
            self.text_frame, 
            wrap="word", 
            undo=True, 
            bg=bg_color, 
            fg=fg_color,
            width=80,  # Characters wide
            height=30  # Lines tall
        )
        self.text_area.pack(fill=tk.BOTH, expand=True)

        # Track the current font for new text
        self.current_font = ("Arial", 12)
        self.text_area.configure(font=self.current_font)

        # Create a tag for the current font
        self.text_area.tag_configure("current_font", font=self.current_font)

        # Bind key press to apply the current font to new text
        self.text_area.bind("<KeyPress>", lambda event: self.apply_current_font("current_font"))

        # Create menu bar
        self.create_menu()

        # Apply theme
        self.theme_manager.apply_theme(root, self.theme_manager.current_theme)

    def show_message(self, message, title="Notification", error=False):
        MessagePopup(self.root, message, title, error)

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
        file_menu.add_command(label="Print", command=self.print_text)  # Add this line
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

        # Add "Change Selected Text Font" option
        text_menu.add_command(label="Change Selected Text Font", command=self.change_selected_text_font)
        
        menu_bar.add_cascade(label="Text", menu=text_menu)

        self.root.config(menu=menu_bar)

    def print_text(self):
        """Print the content of the text area."""
        import tempfile
        import os
        import subprocess
        
        # Get the text content
        text_content = self.text_area.get("1.0", tk.END)
        
        # Create a temporary file
        with tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix='.txt') as tmp_file:
            tmp_file.write(text_content)
            tmp_file_path = tmp_file.name
        
        try:
            # Platform-independent printing (works on Windows, macOS, and Linux)
            if os.name == 'nt':  # Windows
                os.startfile(tmp_file_path, 'print')
            elif os.name == 'posix':
                if os.uname().sysname == 'Darwin':  # macOS
                    subprocess.run(['lp', tmp_file_path])
                else:  # Linux
                    subprocess.run(['lpr', tmp_file_path])
        finally:
            # Clean up - delete the temporary file after a short delay
            self.root.after(10000, lambda: os.unlink(tmp_file_path))

    def new_file(self):
        """Clears the text area to start a new file."""
        self.text_area.delete(1.0, tk.END)

    def open_file(self):
        """Opens a text file and loads it into the text area."""
        file_path = filedialog.askopenfilename(
            filetypes=[("Text Data Files", "*.tdat"), ("Text Files", "*.txt"), ("All Files", "*.*")]
        )
        if not file_path:
            return

        self.text_area.delete(1.0, tk.END)

        if file_path.endswith('.tdat'):
            # Load JSON data and apply tags
            import json
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    text_content = data.get('text', '')
                    tags_data = data.get('tags', [])

                    self.text_area.insert(tk.END, text_content)

                    for tag_info in tags_data:
                        tag_name = tag_info['name']
                        font_family = tag_info['font_family']
                        font_size = tag_info['font_size']
                        ranges = tag_info['ranges']

                        # Configure the tag
                        self.text_area.tag_configure(tag_name, font=(font_family, font_size))

                        # Apply ranges
                        for start, end in ranges:
                            self.text_area.tag_add(tag_name, start, end)

                    # Update current_font if loaded
                    if 'current_font' in self.text_area.tag_names():
                        font_str = self.text_area.tag_cget('current_font', 'font')
                        parts = font_str.split()
                        if len(parts) >= 2:
                            try:
                                self.current_font = (' '.join(parts[:-1]), int(parts[-1]))
                            except ValueError:
                                pass

            except Exception as e:
                self.show_message(f"Error loading file: {str(e)}", title="Error", error=True)
        else:
            # Load plain text and apply current font
            with open(file_path, 'r') as f:
                self.text_area.insert(tk.END, f.read())
                self.text_area.tag_add("current_font", "1.0", "end")

    def save_file(self):
        """Saves the current content to a file."""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".tdat",
            filetypes=[("Text Data Files", "*.tdat"), ("Text Files", "*.txt"), ("All Files", "*.*")]
        )
        if not file_path:
            return

        text_content = self.text_area.get("1.0", tk.END).rstrip('\n')  # Remove trailing newline added by tk.END

        if file_path.endswith('.tdat'):
            # Save as JSON with font tags
            tags_data = []
            for tag_name in self.text_area.tag_names():
                if tag_name.startswith('font_') or tag_name == 'current_font':
                    font_family, font_size = None, None
                    if tag_name == 'current_font':
                        # Extract font from tag configuration
                        font_str = self.text_area.tag_cget(tag_name, 'font')
                        parts = font_str.split()
                        if len(parts) < 1:
                            continue
                        try:
                            font_size = int(parts[-1])
                            font_family = ' '.join(parts[:-1])
                        except ValueError:
                            continue
                    else:
                        # Extract font from tag name
                        parts = tag_name.split('_')
                        font_family = ' '.join(parts[1:-1])
                        try:
                            font_size = int(parts[-1])
                        except ValueError:
                            continue

                    # Collect ranges for the tag
                    ranges = self.text_area.tag_ranges(tag_name)
                    range_pairs = []
                    for i in range(0, len(ranges), 2):
                        start = str(ranges[i])
                        end = str(ranges[i+1])
                        range_pairs.append([start, end])

                    tags_data.append({
                        'name': tag_name,
                        'font_family': font_family,
                        'font_size': font_size,
                        'ranges': range_pairs
                    })

            data = {
                'text': text_content,
                'tags': tags_data
            }

            import json
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=4)
        else:
            # Save as plain text
            with open(file_path, 'w') as f:
                f.write(text_content)

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

    def change_selected_text_font(self):
        """Change the font of the currently selected text."""
        try:
            # Get the currently selected text
            sel_start = self.text_area.index(tk.SEL_FIRST)
            sel_end = self.text_area.index(tk.SEL_LAST)
            
            # Ask user to select a font
            selected_font = self.ask_font()
            if selected_font:
                # Create a unique tag for this font change
                font_tag = f"font_{selected_font[0]}_{selected_font[1]}"
                self.text_area.tag_configure(font_tag, font=selected_font)
                
                # Apply the tag to the selected text
                self.text_area.tag_add(font_tag, sel_start, sel_end)
                
        except tk.TclError:
            # No text selected
            self.show_message("Please select some text first", title="Error", error=True)

    def ask_font(self):
        """Open a dialog to select font and size."""
        # Create a simple font selection dialog
        font_dialog = tk.Toplevel(self.root)
        font_dialog.title("Select Font")
        
        # Font family selection
        tk.Label(font_dialog, text="Font:").grid(row=0, column=0, padx=5, pady=5)
        font_family = tk.StringVar(value="Arial")
        font_list = tk.Listbox(font_dialog, height=5, exportselection=0)
        for f in ["Arial", "Times New Roman", "Courier New", "Verdana", "Comic Sans MS"]:
            font_list.insert(tk.END, f)
        font_list.grid(row=0, column=1, padx=5, pady=5)
        font_list.selection_set(0)
        
        # Font size selection
        tk.Label(font_dialog, text="Size:").grid(row=1, column=0, padx=5, pady=5)
        font_size = tk.IntVar(value=12)
        size_entry = tk.Entry(font_dialog, textvariable=font_size)
        size_entry.grid(row=1, column=1, padx=5, pady=5)
        
        # OK button
        selected_font = []
        def on_ok():
            selected_font.append((font_list.get(font_list.curselection()), font_size.get()))
            font_dialog.destroy()
            
        tk.Button(font_dialog, text="OK", command=on_ok).grid(row=2, column=1, pady=10)
        
        # Make the dialog modal
        font_dialog.transient(self.root)
        font_dialog.grab_set()
        self.root.wait_window(font_dialog)
        
        return selected_font[0] if selected_font else None