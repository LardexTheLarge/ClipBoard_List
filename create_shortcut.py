import os
import sys
from pathlib import Path
import winshell
from win32com.client import Dispatch

def create_shortcut():
    desktop = winshell.desktop()
    path = os.path.join(desktop, "ClipboardManager.lnk")
    target = sys.executable
    wDir = str(Path(__file__).parent)
    icon = str(Path(__file__).parent / 'icon.ico')
    script = str(Path(__file__).parent / 'clipboard_manager.py')

    shell = Dispatch('WScript.Shell')
    shortcut = shell.CreateShortCut(path)
    shortcut.Targetpath = target
    shortcut.WorkingDirectory = wDir
    shortcut.IconLocation = icon
    shortcut.Arguments = f'"{script}"'  # Ensure the script path is quoted
    shortcut.save()

    print(f"Shortcut created at: {path}")
    print(f"Target: {target}")
    print(f"Arguments: {shortcut.Arguments}")
    print(f"Working Directory: {wDir}")

if __name__ == '__main__':
    create_shortcut()
