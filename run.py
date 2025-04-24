import streamlit.web.cli as stcli
import os, sys
from utils_update import resolve_path, update_setuptools, update_repository, check_and_fix_requirements, find_available_port

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
            '--global.developmentMode=true',
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

