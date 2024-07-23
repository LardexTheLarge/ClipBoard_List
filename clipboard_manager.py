import threading
import tkinter as tk
import sys
import traceback
import time
import os

from utils.clipboard_classes import ClipboardManager, ClipboardApp

def log_error():
    with open("error_log.txt", "w") as f:
        f.write("An error occurred:\n")
        traceback.print_exc(file=f)

# Initialize logging at the start
try:
    with open("log.txt", "w") as f:
        f.write("Starting clipboard manager script...\n")
        f.write(f"Arguments: {sys.argv}\n")
        f.write(f"Current working directory: {os.getcwd()}\n")

    print("Clipboard Manager script started")
    print("Arguments:", sys.argv)
    print("Current working directory:", os.getcwd())

    clipboard_manager = ClipboardManager()

    # Run the clipboard monitoring in a separate thread
    monitor_thread = threading.Thread(target=clipboard_manager.monitor_clipboard)
    monitor_thread.daemon = True
    monitor_thread.start()

    root = tk.Tk()
    app = ClipboardApp(root, clipboard_manager)
    root.mainloop()
except Exception as e:
    log_error(e)
    with open("log.txt", "a") as f:
        f.write("An exception occurred. See error_log.txt for details.\n")

# Pause at the end to keep the console open
print("Press Enter to exit...")
input()