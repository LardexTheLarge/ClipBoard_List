import threading
import tkinter as tk
from utils.clipboard_classes import ClipboardManager, ClipboardApp


clipboard_manager = ClipboardManager()

# Run the clipboard monitoring in a separate thread
monitor_thread = threading.Thread(target=clipboard_manager.monitor_clipboard)
monitor_thread.daemon = True
monitor_thread.start()

root = tk.Tk()
app = ClipboardApp(root, clipboard_manager)
root.mainloop()

