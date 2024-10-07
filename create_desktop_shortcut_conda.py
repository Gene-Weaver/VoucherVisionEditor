import os
import sys
import win32com.client
import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageEnhance

def create_shortcut():
    # Request user's confirmation
    confirmation = input("Do you want to create a shortcut for the VoucherVision Editor? (y/n): ")

    if confirmation.lower() != "y":
        print("Okay, no shortcut will be created.")
        return

    # Get the script path
    script_path = os.path.abspath(__file__)
    script_dir = os.path.abspath(os.path.dirname(script_path))

    # Path to the icon file
    icon_path = os.path.join(script_dir, 'img', 'icon.jpg')
    img = Image.open(icon_path)
    enhancer = ImageEnhance.Color(img)
    img_enhanced = enhancer.enhance(1.5)
    img_enhanced.save(os.path.join(script_dir, 'img', 'icon.ico'), format='ICO', sizes=[(256, 256)])
    icon_path_ico = os.path.join(script_dir, 'img', 'icon.ico')

    # Ask for the name of the shortcut
    shortcut_name = "VV Editor"

    root = tk.Tk()
    root.withdraw()  # Hide the main window

    root.update()  # Ensures that the dialog appears on top
    folder_path = filedialog.askdirectory(title="Choose location to save the shortcut")
    print(f"Shortcut will be saved to {folder_path}")

    # Get Conda environment name
    env_name = input("Enter the name of your Conda environment: ")

    # The path to Miniforge's activate.bat script (hardcoded based on your setup)
    conda_activate_bat = r"C:\ProgramData\miniforge3\Scripts\activate.bat"

    # Create the command to activate the environment and run the Python script
    conda_activate_cmd = f'"{conda_activate_bat}" "{env_name}"'
    python_run_cmd = f'cd /D "{script_dir}" && python run.py'

    # Combine the commands into one string
    final_cmd = f'{conda_activate_cmd} && {python_run_cmd}'

    # Create a Windows shortcut
    shortcut_path = os.path.join(folder_path, f'{shortcut_name}.lnk')

    shell = win32com.client.Dispatch("WScript.Shell")
    shortcut = shell.CreateShortCut(shortcut_path)

    # Set the Windows command processor (cmd.exe) as the TargetPath
    shortcut.Targetpath = "%windir%\\System32\\cmd.exe"

    # Pass the final command as an argument to cmd.exe
    shortcut.Arguments = f'/K {final_cmd}'

    # Set the icon of the shortcut
    shortcut.IconLocation = icon_path_ico
    shortcut.save()

    print(f"Shortcut created with the name '{shortcut_name}' in the chosen directory.")

if __name__ == "__main__":
    create_shortcut()
