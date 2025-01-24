import threading
import tkinter as tk
import sys
import traceback
import os
import logging

from utils.app_launcher_classes import AppLauncher


if __name__ == "__main__":
    root = tk.Tk()
    app_launcher = AppLauncher(root)
    root.mainloop()
