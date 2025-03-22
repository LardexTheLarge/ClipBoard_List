import tkinter as tk
from utils.text_editor import TextEditorApp


if __name__ == "__main__":
    root = tk.Tk()
    app_launcher = TextEditorApp(root)
    root.mainloop()