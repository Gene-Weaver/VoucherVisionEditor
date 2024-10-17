# https://ploomber.io/blog/streamlit_exe/

# https://medium.com/@sathiyamurthi239/how-to-create-a-streamlit-executable-python-to-exe-3bcb8eed9b16
# pip install --upgrade cx_Freeze
# cxfreeze -c run.py 
# pip install protobuf==3.20.0

import streamlit.web.cli as stcli
import os, sys
import socket

def find_available_port(start_port, max_attempts=1000):
    port = start_port
    attempts = 0
    while attempts < max_attempts:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(('127.0.0.1', port))
                # If successful, return the current port
                return port
            except socket.error:
                # If the port is in use, increment the port number and try again
                port += 1
                attempts += 1
    # Optional: Return None or raise an exception if no port is found within the attempts limit
    raise ValueError(f'Could not find an available port within {max_attempts} attempts starting from port {start_port}.')


def resolve_path(path):
    resolved_path = os.path.abspath(os.path.join(os.getcwd(), path))
    return resolved_path


if __name__ == '__main__':
    start_port = 8589
    try:
        free_port = find_available_port(start_port)
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
        print(e)
        
        
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
