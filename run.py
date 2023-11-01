# https://ploomber.io/blog/streamlit_exe/

# https://medium.com/@sathiyamurthi239/how-to-create-a-streamlit-executable-python-to-exe-3bcb8eed9b16
# pip install --upgrade cx_Freeze
# cxfreeze -c run.py 

import streamlit.web.cli as stcli
import os, sys


def resolve_path(path):
    resolved_path = os.path.abspath(os.path.join(os.getcwd(), path))
    return resolved_path


if __name__ == "__main__":
    sys.argv = [
        "streamlit",
        "run",
        resolve_path("VoucherVisionEditor.py"),
        "--global.developmentMode=false",
        "--server.port=8523",
    ]
    sys.exit(stcli.main())