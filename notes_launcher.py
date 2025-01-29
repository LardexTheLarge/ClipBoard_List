import tkinter as tk
from utils.notes_class import NoteTakerApp


# Main application
if __name__ == "__main__":
    root = tk.Tk()
    app = NoteTakerApp(root)
    root.mainloop()