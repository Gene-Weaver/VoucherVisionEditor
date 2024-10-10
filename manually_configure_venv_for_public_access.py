import os
import shutil

def edit_pyvenv_cfg():
    # Get the directory where the script is located
    script_dir = os.path.dirname(__file__)
    
    # Path to the pyvenv.cfg file inside ./.venv_VVE
    venv_cfg_path = os.path.join(script_dir, ".venv_VVE", "pyvenv.cfg")
    
    # Check if the file exists
    if not os.path.exists(venv_cfg_path):
        print(f"Error: {venv_cfg_path} not found.")
        return

    # Ask the user if they want to configure the pyvenv.cfg file
    user_response = input("Do you want to manually configure the pyvenv.cfg file? (yes/no): ").strip().lower()
    
    if user_response != 'yes':
        print("No changes made to the pyvenv.cfg file.")
        return
    
    # Backup the original pyvenv.cfg as pyvenv_ORIGINAL.cfg
    backup_cfg_path = os.path.join(script_dir, ".venv_VVE", "pyvenv_ORIGINAL.cfg")
    shutil.copyfile(venv_cfg_path, backup_cfg_path)
    print(f"Backup created at {backup_cfg_path}")
    
    # Prompt the user for the public Python installation folder and version
    python_home = input("Enter the path to the public Python installation folder (e.g., C:\\Program Files\\Python312): ").strip()
    python_version = input("Enter the specific Python version (e.g., 3.12.7150.0): ").strip()
    
    # Generate the new configuration content
    new_cfg_content = f"""home = {python_home}
include-system-site-packages = false
version = {python_version}
executable = {python_home}\\python.exe
command = {python_home}\\python.exe -m venv C:\\Users\\Public\\Documents\\VoucherVisionEditor\\.venv_VVE
"""
    
    # Write the new configuration to the pyvenv.cfg file
    with open(venv_cfg_path, 'w') as cfg_file:
        cfg_file.write(new_cfg_content)
    
    print(f"The pyvenv.cfg file has been successfully updated at {venv_cfg_path}")

if __name__ == "__main__":
    edit_pyvenv_cfg()
