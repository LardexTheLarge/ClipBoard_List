import tkinter as tk
from utils.app_launcher_classes import AppLauncher


if __name__ == "__main__":
    root = tk.Tk()
    app_launcher = AppLauncher(root)
    root.mainloop()