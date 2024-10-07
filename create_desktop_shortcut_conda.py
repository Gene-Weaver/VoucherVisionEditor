import os
import sys
import win32com.client
import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageEnhance
import subprocess

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

    # Allow user to select Conda executable
    conda_exe = filedialog.askopenfilename(title="Locate your conda executable (usually conda.exe)", filetypes=[("Executable", "*.exe")])
    print(f"Using Conda executable located at {conda_exe}")

    # Allow user to choose if the environment is in a shared location or user-specific
    env_location = filedialog.askdirectory(title="Select the location of your Conda environment (shared or user-specific)")
    print(f"Using Conda environment located at {env_location}")

    # Step 1: Find the Miniforge bash terminal executable
    # Assuming Miniforge bash is installed in a standard location
    miniforge_bash = filedialog.askopenfilename(title="Locate your Miniforge bash executable (bash.exe or mintty.exe)", filetypes=[("Executable", "*.exe")])

    # Step 2: Create the command to activate the environment and run the Python script
    conda_activate_cmd = f'source "{os.path.join(env_location, "bin/activate")}" && conda activate "{env_name}"'
    python_run_cmd = f'cd "{script_dir}" && python run.py'

    # Combine the commands into a bash command
    bash_cmd = f'{conda_activate_cmd} && {python_run_cmd}'

    # Step 3: Create a Windows shortcut
    shortcut_path = os.path.join(folder_path, f'{shortcut_name}.lnk')

    shell = win32com.client.Dispatch("WScript.Shell")
    shortcut = shell.CreateShortCut(shortcut_path)
    
    # Set the Miniforge terminal as the TargetPath
    shortcut.Targetpath = miniforge_bash

    # Pass the bash command as an argument to the Miniforge terminal
    shortcut.Arguments = f'-c "{bash_cmd}"'

    # Set the icon of the shortcut
    shortcut.IconLocation = icon_path_ico
    shortcut.save()

    print(f"Shortcut created with the name '{shortcut_name}' in the chosen directory.")

if __name__ == "__main__":
    create_shortcut()
