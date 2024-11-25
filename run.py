# https://ploomber.io/blog/streamlit_exe/

# https://medium.com/@sathiyamurthi239/how-to-create-a-streamlit-executable-python-to-exe-3bcb8eed9b16
# pip install --upgrade cx_Freeze
# cxfreeze -c run.py 
# pip install protobuf==3.20.0

import streamlit.web.cli as stcli
import os, sys, random, time, subprocess
import socket
from pathlib import Path
import git
from importlib.metadata import distribution

# def update_repository():
#     try:
#         # Run 'git pull' to update the repository
#         result = subprocess.run(["git", "pull"], capture_output=True, text=True, check=True)
#         print(result.stdout)
#         if result.returncode == 0:
#             print("Repository updated successfully.")
#         else:
#             print("Failed to update the repository.")
#     except subprocess.CalledProcessError as e:
#         print(f"Error updating repository: {e.stderr}")
#         sys.exit(1)
def update_setuptools():
    """Update the setuptools package using pip."""
    print("Updating setuptools to avoid compatibility issues...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "setuptools"], check=True)
        print("setuptools updated successfully.")
    except subprocess.CalledProcessError as e:
        print("Failed to update setuptools:", e)
        sys.exit(1)  # Exit if setuptools can't be updated
        
def check_and_fix_requirements(requirements_file):
    """
    Checks if installed packages in the virtual environment satisfy the requirements specified
    in the requirements.txt file and fixes them if they do not.
    """
    # Retrieve installed distributions as a dict with lower-case package names as keys
    installed_distributions = {dist.metadata['Name'].lower(): dist.version for dist in distribution()}

    missing_or_incompatible = []
    
    with open(requirements_file, 'r') as req_file:
        requirements = req_file.readlines()

    # Check each requirement in the file
    for req in requirements:
        req = req.strip()
        if not req or req.startswith('#'):
            continue  # Skip empty lines and comments
        # Assume simple 'pkg==version' format for requirements
        if '==' in req:
            pkg_name, required_version = req.split('==')
        else:
            pkg_name = req
            required_version = None
        
        if pkg_name.lower() not in installed_distributions:
            missing_or_incompatible.append(f"{pkg_name} is not installed")
        elif required_version and installed_distributions[pkg_name.lower()] != required_version:
            installed_version = installed_distributions[pkg_name.lower()]
            missing_or_incompatible.append(f"{pkg_name}=={installed_version} does not satisfy {req}")

    if missing_or_incompatible:
        print("The following packages are missing or incompatible:")
        for issue in missing_or_incompatible:
            print(f"  - {issue}")
        
        print("Attempting to fix the package issues by running 'pip install -r requirements.txt'...")
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "-r", requirements_file], check=True)
            print("Packages have been successfully updated.")
        except subprocess.CalledProcessError as e:
            print("Failed to install packages:", e)
    else:
        print("All requirements are satisfied.")


def find_github_desktop_git():
    """Search for the most recent GitHub Desktop Git installation."""
    # Base path where GitHub Desktop versions are located
    base_path = Path(f"C:/Users/{os.getlogin()}/AppData/Local/GitHubDesktop/")
    print(f"base_path: {base_path}")

    # Searching recursively for git.exe within any directories under the base path
    versions = sorted(base_path.rglob('git.exe'), key=lambda x: x.parent, reverse=True)
    for git_path in versions:
        print(f"git_path: {git_path}")
        if "app-" in str(git_path.parent):  # Ensuring it's in an 'app-' directory if that's still relevant
            print(f"git_path_exists: TRUE")
            return str(git_path)

    print(f"git_path_exists: FALSE")
    return None

def update_repository(repo_path):
    print(f"changing path to: {repo_path}")
    os.chdir(repo_path)
    print(f"changed to: {repo_path}")

    # """Attempts to update the repository using the system's git or GitHub Desktop's git."""
    # try:
    #     # Try using the system's git command
    #     result = subprocess.run(["git", "pull"], capture_output=True, text=True, check=True)
    #     print(result.stdout)
    #     if result.returncode == 0:
    #         print("Repository updated successfully.")
    # except Exception as e:
    #     print(f"Error updating repository with system Git: {e}")
        # Fallback: use GitHub Desktop's Git executable
    try:
        # Open the existing repository at the specified path
        repo = git.Repo(repo_path)
        # Check for the current working branch
        current_branch = repo.active_branch
        print(f"Updating repository on branch: {current_branch.name}")

        # Pulls updates for the current branch
        origin = repo.remotes.origin
        result = origin.pull()

        # Check if the pull was successful
        if result[0].flags > 0:
            print("Repository updated successfully.")
        else:
            print("No updates were available.")
                
    except Exception as e:
        print(f"Error while updating repository: {e}")

def find_available_port(start_port, end_port):
    ports = list(range(start_port, end_port + 1))
    random.shuffle(ports)
    for port in ports:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(("127.0.0.1", port))
                return port
            except socket.error:
                print(f"Port {port} is in use, trying another port...")
    raise ValueError(f"Could not find an available port in the range {start_port}-{end_port}.")


def resolve_path(path):
    resolved_path = os.path.abspath(os.path.join(os.getcwd(), path))
    return resolved_path


if __name__ == '__main__':
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    start_port = 8501
    end_port = 8599
    retry_count = 0
    repo_path = resolve_path(os.path.dirname(__file__))
    print(f"repo_path: {repo_path}")

    update_setuptools()
    requirements_file = 'requirements.txt'
    check_and_fix_requirements(resolve_path(os.path.join(os.path.dirname(__file__),'requirements.txt')))

    try:
        update_repository(repo_path)
    except:
        print(f"Could not update VVE using git pull.")
        print(f"Make sure that 'Git' is installed and can be accessed by this user account.")

    # Update again in case the pull introduced a new package
    check_and_fix_requirements(resolve_path(os.path.join(os.path.dirname(__file__),'requirements.txt')))

    try:
        free_port = find_available_port(start_port, end_port)
        sys.argv = [
            'streamlit',
            'run',
            resolve_path(os.path.join(os.path.dirname(__file__),'VoucherVisionEditor.py')),
            '--global.developmentMode=false',
            f'--server.maxUploadSize=51200',
            f'--server.enableStaticServing=true',
            f'--server.runOnSave=true',
            f'--server.port={free_port}',
            f'--theme.primaryColor=#16a616',
            f'--theme.backgroundColor=#1a1a1a',
            f'--theme.secondaryBackgroundColor=#303030',
            f'--theme.textColor=cccccc',
        ]
        sys.exit(stcli.main())


    except ValueError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    else:
        print("Failed to start the application after multiple attempts.")

# https://ploomber.io/blog/streamlit_exe/

# https://medium.com/@sathiyamurthi239/how-to-create-a-streamlit-executable-python-to-exe-3bcb8eed9b16
# pip install --upgrade cx_Freeze
# cxfreeze -c run.py 
# pip install protobuf==3.20.0

# import os
# import sys
# import socket
# import time
# import subprocess
# import random

# def resolve_path(path):
#     resolved_path = os.path.abspath(os.path.join(os.getcwd(), path))
#     return resolved_path
    
# def find_available_port(start_port, end_port):
#     ports = list(range(start_port, end_port + 1))
#     random.shuffle(ports)
#     for port in ports:
#         with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
#             try:
#                 s.bind(("127.0.0.1", port))
#                 return port
#             except socket.error:
#                 print(f"Port {port} is in use, trying another port...")
#     raise ValueError(f"Could not find an available port in the range {start_port}-{end_port}.")

# def find_app_path():
#     # Check if we're running from within a PyInstaller bundle
#     if getattr(sys, 'frozen', False):
#         bundle_dir = sys._MEIPASS
#         app_path = os.path.join(bundle_dir, 'app.py')  # Adjust to relative path in bundle
#     else:
#         app_path = os.path.join(os.getcwd(), 'app.py')  # Original path for non-frozen case

#     if not os.path.exists(app_path):
#         raise FileNotFoundError(f"app.py not found at {app_path}")

#     return app_path

# def get_local_ip():
#     """Get the local IP address of the current machine."""
#     hostname = socket.gethostname()
#     local_ip = socket.gethostbyname(hostname)
#     return local_ip

# def run_streamlit(port):
#     app_path = resolve_path(os.path.join(os.path.dirname(__file__),'VoucherVisionEditor.py'))


#     cmd = [
#         sys.executable,
#         '-m', 'streamlit',
#         'run',
#         app_path,
#         '--global.developmentMode=false',
#         f'--server.maxUploadSize=51200',
#         f'--server.enableStaticServing=true',
#         f'--server.runOnSave=true',
#         f'--server.port={free_port}',
#         f'--theme.primaryColor=#16a616',
#         f'--theme.backgroundColor=#1a1a1a',
#         f'--theme.secondaryBackgroundColor=#303030',
#         f'--theme.textColor=cccccc',
#     ]
#     print(f"Running command: {' '.join(cmd)}")
#     process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1, universal_newlines=True)
#     return process

# if __name__ == "__main__":
#     os.environ['PYTHONIOENCODING'] = 'utf-8'
#     start_port = 8501
#     end_port = 8599
#     max_retries = 5
#     retry_count = 0

#     while retry_count < max_retries:
#         try:
#             free_port = find_available_port(start_port, end_port)
#             local_ip = get_local_ip()
#             print(f"Found available port: {free_port}")
#             print(f"Local IP address: {local_ip}")

#             print(f"VoucherVisionEditor is running in your browser:")
#             print(f"Localhost URL: http://localhost:{free_port}")
#             print(f"Network URL: http://{local_ip}:{free_port}")
            
#             process = run_streamlit(free_port)
            
#             # Wait and capture output
#             start_time = time.time()
#             while time.time() - start_time < 30:  # Wait for up to 30 seconds
#                 output = process.stdout.readline()
#                 if output:
#                     print(output.strip())
#                     if "VoucherVisionEditor is opening in your browser." in output:
#                         print("VoucherVisionEditor started successfully.")
#                         break
#                 if process.poll() is not None:
#                     break
#                 time.sleep(0.1)

#             if process.poll() is None:
#                 # Show both localhost and local IP addresses with the port
#                 print(f"VoucherVisionEditor is running in your browser:")
#                 print(f"Localhost URL: http://localhost:{free_port}")
#                 print(f"Network URL: http://{local_ip}:{free_port}")
#                 while process.poll() is None:
#                     time.sleep(1)
#                 print("VoucherVisionEditor ended.")
#                 break
#             else:
#                 stdout, stderr = process.communicate()
#                 print(f"VoucherVisionEditor failed to start. Error:\n{stderr}")

#         except ValueError as e:
#             print(f"Error: {e}")
#         except Exception as e:
#             print(f"An unexpected error occurred: {e}")
        
#         retry_count += 1
#         if retry_count < max_retries:
#             print(f"Retrying... (Attempt {retry_count} of {max_retries})")
#             time.sleep(2)
#         else:
#             print("Failed to start the application after multiple attempts.")

#     print("Press Enter to exit...")
#     input()
