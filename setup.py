from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need fine-tuning.
build_exe_options = {
    "packages": ["os", "streamlit", "pyarrow"],  # add other packages if needed
    "excludes": []  # add packages you want to exclude if needed
}

base = None

setup(
    name="VoucherVisionEditor",
    version="0.1",
    description="Voucher Vision Editor App",
    options={"build_exe": build_exe_options},
    executables=[Executable("run.py", base=base)]
)
