# https://ploomber.io/blog/streamlit_exe/

# https://medium.com/@sathiyamurthi239/how-to-create-a-streamlit-executable-python-to-exe-3bcb8eed9b16
# pip install --upgrade cx_Freeze
# cxfreeze -c run.py 

import streamlit.web.cli as stcli
import os, sys


def resolve_path(path):
    resolved_path = os.path.abspath(os.path.join(os.getcwd(), path))
    return resolved_path


    # pip install protobuf==3.20.0

if __name__ == "__main__":
    port = 8530
    
    try:
        sys.argv = [
            "streamlit",
            "run",
            resolve_path(os.path.join(os.path.dirname(__file__),"VoucherVisionEditor.py")),
            "--global.developmentMode=false",
            f"--server.port={port}",
        ]
    except:
        port += 1
        sys.argv = [
            "streamlit",
            "run",
            resolve_path(os.path.join(os.path.dirname(__file__),"VoucherVisionEditor.py")),
            "--global.developmentMode=false",
            f"--server.port={port}",
        ]
    sys.exit(stcli.main())