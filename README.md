[![VoucherVisionEditor](https://LeafMachine.org/img/VVE_Logo.png "VoucherVisionEditor")](https://LeafMachine.org/)

Table of Contents
=================

* [Table of Contents](#table-of-contents)
* [VoucherVisionEditor](#vouchervisioneditor-user-interface-for-vouchervision)
* [Try our public demo!](#try-our-public-demo)
* [Installing VoucherVisionEditor](#installing-VoucherVisionEditor)
   * [Prerequisites](#prerequisites)
   * [Installation - Cloning the VoucherVisionEditor Repository](#installation---cloning-the-VoucherVisionEditor-repository)
   * [About Python Virtual Environments](#about-python-virtual-environments)
   * [Installation - Ubuntu 20.04](#installation---ubuntu-2004)
      * [Virtual Environment](#virtual-environment)
      * [Installing Packages](#installing-packages)
   * [Installation - Windows 10+](#installation---windows-10)
      * [Virtual Environment](#virtual-environment-1)
      * [Conda Environment](#conda-environment)
      
      * [Installing Packages](#installing-packages-1)
* [Create a Desktop Shortcut to Launch VoucherVisionEditor GUI](#create-a-desktop-shortcut-to-launch-vouchervisioneditor-gui)
* [Running VoucherVisionEditor from the Terminal](#running-vouchervisioneditor-from-the-terminal)

---

# VoucherVisionEditor: User Interface for VoucherVision
This application serves as a dedicated user interface designed to efficiently edit and manage the automatically generated label transcriptions by VoucherVision. VoucherVision, a significant module of LeafMachine2, leverages cutting-edge Natural Language Processing (NLP) technologies to transcribe labels attached to natural history collection specimens, including those found on herbarium vouchers.

## Powered by Large Language Models
At its core, VoucherVision employs several Large Language Models (LLMs) such as OpenAI's ChatGPT, Google's PaLM, and other locally-hosted LLMs that have been fine-tuned on transcription groundtruth datasets and GBIF records. This selection of potent models ensures optimal transcription quality across diverse datasets and provides flexibility in terms of cost and computational requirements. 

## Comprehensive Error Correction
To guarantee the generation of valid responses, VoucherVision integrates robust error correction procedures that enhance the reliability of the LLMs. This way, we ensure the integrity and accuracy of the transcriptions and support high-quality data management.

## Customization
Both VoucherVision and VoucherVisionEditor are built with adaptability in mind. They can be easily customized to accommodate varying digitization requirements - from basic to advanced, including full Darwin Core Archive fields. This adaptability makes our software suitable for a wide range of digitization efforts.

---

# Try our public demo!
Our public demo, while lacking several quality control and reliability features found in the full VoucherVision module, provides an exciting glimpse into its capabilities. Feel free to upload your herbarium specimen and see what happens! We make frequent updates, so don't forget to revisit!
[VoucherVision Demo](https://huggingface.co/spaces/phyloforfun/VoucherVision)

---

# Installing VoucherVisionEditor

## Prerequisites
- Python 3.12 or later 

## Installation - Cloning the VoucherVisionEditor Repository
1. First, install Python 3.12, or greater, on your machine of choice. We have validated with Python 3.8, but some of the packages in the requirements will need to be relaxed, just remove the versions and let the package manager get the older versions that are compatible with the older Python.
    - Make sure that you can use `pip` to install packages on your machine, or at least inside of a virtual environment.
    - Simply type `pip` into your terminal or PowerShell. If you see a list of options, you are all set. Otherwise, see
    either this [PIP Documentation](https://pip.pypa.io/en/stable/installation/) or [this help page](https://www.geeksforgeeks.org/how-to-install-pip-on-windows/)
2. Open a terminal window and `cd` into the directory where you want to install VoucherVisionEditor.
3. In the [Git BASH terminal](https://gitforwindows.org/), clone the VoucherVisionEditor repository from GitHub by running the command:
    <pre><code class="language-python">git clone https://github.com/Gene-Weaver/VoucherVisionEditor.git</code></pre>
    <button class="btn" data-clipboard-target="#code-snippet"></button>
4. Move into the VoucherVisionEditor directory by running `cd VoucherVisionEditor` in the terminal.
5. To run VoucherVisionEditor we need to install its dependencies inside of a python virtual environmnet. Follow the instructions below for your operating system. 

## About Python Virtual Environments
A virtual environment is a tool to keep the dependencies required by different projects in separate places, by creating isolated python virtual environments for them. This avoids any conflicts between the packages that you have installed for different projects. It makes it easier to maintain different versions of packages for different projects.

For more information about virtual environments, please see [Creation of virtual environments](https://docs.python.org/3/library/venv.html)

---

## Installation - Ubuntu and MacOS

### Virtual Environment

1. Still inside the VoucherVisionEditor directory, show that a venv is currently not active 
    <pre><code class="language-python">which python</code></pre>
    <button class="btn" data-clipboard-target="#code-snippet"></button>
    For Mac:
    <pre><code class="language-python">python --version</code></pre>
    <button class="btn" data-clipboard-target="#code-snippet"></button>
2. Then create the virtual environment (.venv_VVE is the name of our new virtual environment)  
    <pre><code class="language-python">python3 -m venv .venv_VVE</code></pre>
    <button class="btn" data-clipboard-target="#code-snippet"></button>
    Or...
    <pre><code class="language-python">python -m venv .venv_VVE</code></pre>
    <button class="btn" data-clipboard-target="#code-snippet"></button>
3. Activate the virtual environment  
    <pre><code class="language-python">source ./.venv_VVE/bin/activate</code></pre>
    <button class="btn" data-clipboard-target="#code-snippet"></button>
4. Confirm that the venv is active (should be different from step 1)  
    <pre><code class="language-python">which python</code></pre>
    <button class="btn" data-clipboard-target="#code-snippet"></button>
    For Mac:
    <pre><code class="language-python">python --version</code></pre>
    <button class="btn" data-clipboard-target="#code-snippet"></button>
5. If you want to exit the venv, deactivate the venv using  
    <pre><code class="language-python">deactivate</code></pre>
    <button class="btn" data-clipboard-target="#code-snippet"></button>

### Installing Packages

1. Install the required libraries to use VoucherVisionEditor 
    <pre><code class="language-python">pip install -r requirements.txt</code></pre>
    <button class="btn" data-clipboard-target="#code-snippet"></button>

2. Upgrade Streamlit 
    <pre><code class="language-python">pip install --upgrade streamlit</code></pre>
    <button class="btn" data-clipboard-target="#code-snippet"></button>

---

## Installation - Windows 10+

### Virtual Environment
> Note: we assume that you have WSL already installed. Please see [the Microsoft help page](https://learn.microsoft.com/en-us/windows/wsl/install) if the steps below cause errors.
1. Still inside the VoucherVisionEditor directory, show that a venv is currently not active 
    <pre><code class="language-python">python --version</code></pre>
    <button class="btn" data-clipboard-target="#code-snippet"></button>
2. Then create the virtual environment (.venv_VVE is the name of our new virtual environment)  
    <pre><code class="language-python">python3 -m venv .venv_VVE </code></pre>
    <button class="btn" data-clipboard-target="#code-snippet"></button>
    Or...
    <pre><code class="language-python">python -m venv .venv_VVE</code></pre>
    <button class="btn" data-clipboard-target="#code-snippet"></button>
3. Activate the virtual environment  
    <pre><code class="language-python">.\.venv_VVE\Scripts\activate</code></pre>
    <button class="btn" data-clipboard-target="#code-snippet"></button>
4. Confirm that the venv is active (should be different from step 1)  
    <pre><code class="language-python">python --version</code></pre>
    <button class="btn" data-clipboard-target="#code-snippet"></button>
5. If you want to exit the venv, deactivate the venv using  
    <pre><code class="language-python">deactivate</code></pre>
    <button class="btn" data-clipboard-target="#code-snippet"></button>

### Installing Packages

1. Install the required dependencies to use VoucherVisionEditor  
    <pre><code class="language-python">pip install -r requirements.txt</code></pre>
    <button class="btn" data-clipboard-target="#code-snippet"></button>

2. Upgrade Streamlit 
    <pre><code class="language-python">pip install --upgrade streamlit</code></pre>
    <button class="btn" data-clipboard-target="#code-snippet"></button>

3. Install pywin32 
    <pre><code class="language-python">pip install pywin32</code></pre>
    <button class="btn" data-clipboard-target="#code-snippet"></button>

---

### Conda Environment
> Note: We assume that you have Conda installed. If not, please follow [this guide](https://docs.conda.io/projects/conda/en/latest/user-guide/install/index.html) to install Conda.

> Make sure that you can use conda from Windows Powershell, not just the conda terminal. Try running the following in the conda terminal:
    ```bash
    conda init powershell  
    ```

1. First, ensure you are inside the `VoucherVisionEditor` directory. You can check if Conda is installed by running:
    ```bash
    conda --version
    ```

2. Create a new Conda environment:
    ```bash
    conda create --name .venv_VVE python=3.11 -y
    ```

    OR Modify this command to install the env in a public location (if multiple users want to access VV Editor)
    ```bash
    conda create --prefix C:\ProgramData\miniforge3\envs\.venv_VVE python=3.11 --yes
    ```

3. Activate the Conda environment:
    ```bash
    conda activate .venv_VVE
    ```
    
    OR if in shared location, modify the following (Step 2 will tell you your exact command to activate):
    ```bash
    conda activate C:\ProgramData\miniforge3\envs\.venv_VVE
    ```

4. Confirm that the Conda environment is active:
    ```bash
    python --version
    ```

5. If you want to deactivate the environment, use:
    ```bash
    conda deactivate
    ```

### Installing Packages

1. Make sure that you `cd` into the `VoucherVisionEditor` cloned repo directory. 

2. Install the required dependencies for `VoucherVisionEditor`:
    ```bash
    pip install -r requirements.txt
    ```

3. Upgrade Streamlit:
    ```bash
    pip install --upgrade streamlit
    ```

4. Install `pywin32` (needed for Windows shortcut functionality):
    ```bash
    pip install pywin32
    ```

### Creating a Shortcut (Optional)
If you'd like to create a desktop shortcut for launching the application:

1. Run the script to create a shortcut:
    ```bash
    python create_shortcut.py
    ```

2. Follow the on-screen instructions to specify the Conda environment and the location where you want the shortcut to be saved.

---


# Create a Desktop Shortcut to Launch VoucherVisionEditor GUI (Windows)
We can create a desktop shortcut to launch VoucherVisionEditor. In the `../VoucherVisionEditor/` directory is a file called `create_desktop_shortcut.py`. In the terminal, move into the `../VoucherVisionEditor/` directory and type:
<pre><code class="language-python">python create_desktop_shortcut.py</code></pre>
<button class="btn" data-clipboard-target="#code-snippet"></button>
Or...
<pre><code class="language-python">python3 create_desktop_shortcut.py</code></pre>
<button class="btn" data-clipboard-target="#code-snippet"></button>
Follow the instructions, select where you want the shortcut to be created, then where the virtual environment is located. 

***Note*** If you ever see an error that says that a "port is not available", open `run.py` in a plain text editor and change the `--port` value to something different but close, like 8502. Sometimes the connection may not close properly. Also make sure that the previous terminal is closed before re-launching.

---
# Create a Desktop Shortcut to Launch VoucherVisionEditor GUI (MacOS)
We can create a desktop shortcut to launch VoucherVisionEditor. In the `../VoucherVisionEditor/` directory is a file called `create_desktop_shortcut_mac.py`. In the terminal, `cd` into the `../VoucherVisionEditor/` directory and type:
<pre><code class="language-python">python create_desktop_shortcut_mac.py</code></pre>
<button class="btn" data-clipboard-target="#code-snippet"></button>
Or...
<pre><code class="language-python">python3 create_desktop_shortcut_mac.py</code></pre>
<button class="btn" data-clipboard-target="#code-snippet"></button>
Now go look in the `../VoucherVisionEditor/` directory. You will see a new file called `VoucherVisionEditor.app`. Drag this file into the `Applications` folder so that you can open VoucherVisionEditor just like any other app. 

***Note*** If you ever see an error that says that a "port is not available", open `run.py` in a plain text editor and change the `--port` value to something different but close, like 8502. Sometimes the connection may not close properly. Also make sure that the previous terminal is closed before re-launching.

---

# Launching VoucherVisionEditor from the Terminal
`cd` into your VoucherVisionEditor directory. 
<pre><code class="language-python">python run.py</code></pre>
<button class="btn" data-clipboard-target="#code-snippet"></button>
OR...
<pre><code class="language-python">./run.py</code></pre>
<button class="btn" data-clipboard-target="#code-snippet"></button>
OR...
<pre><code class="language-python">python ./run.py</code></pre>
<button class="btn" data-clipboard-target="#code-snippet"></button>

<!-- 
We recommend using `python run.py` to launch the GUI, but the following instructions show how to launch via the `streamlit` command, which you probably do not need to worry about.

1. In the terminal, move into the VoucherVisionEditor directory.
2. Make sure that your local version is updated by running `git pull` (you might need to use the Git Bash terminal).
3. We will launch VVE from the terminal. There are two primary flags for the launch command.
---
`--save-dir` defines where the edited file will be saved. VVE never overwrites the original transcription file. This must be the full file path to where 
the edited transcription.xlsx should be saved. If you need to pause an editing run and resume it at a later time, then the last "edited" file becomes the 
new input file, but `--save-dir` can remain the same because it will simply increment after each session. 

---
`--base-path` reroutes the file paths in the original transcription file is the files have been moved. The original transcription file saves the fill paths to the transcription JSON files, cropped labels images, and the original full specimen images. If the computerwhere VVE is running has access to these files and those file locations have not changed, then the `--base-path` option is not needed. But in the even that the original file paths are broken, this will rebuild the file paths to the new locations. 
### Example:
Say that you process images with VoucherVision and the output files are saved to `C:/user/documents/Project_1/Run_1`. The folder `Run_1` contains the main output directories, including the `Original_Images` and `Transcription` folders. To make the output portable, we would copy and move everything inside of the `Project_1` folder. Now the new location might be something like `E:/usr/home/Project_1/Run_1`. So for the `--base=path` option we would include eveerything in the new file path up to the `Transcription` like this:
`--base-path E:/usr/home/Project_1/Run_1`
<pre><code class="language-python">python3 LeafMachine2.py</code></pre>
<button class="btn" data-clipboard-target="#code-snippet"></button> -->
---

# Getting started
1. VoucherVisionEditor launches projects from within the `VoucherVisionEditor/projects` folder. Use the file uploader to drag and drop the `.zip` file for the project that you want to work on.
2. This adds the project to the `/projects` folder. You only have to do this once. Now all material for that project is available to VV Editor.
3. In the dropdown menu, select the project that you want to edit.
4. In the second dropdown, choose the transcription file that you want to edit.
    - For new projects, select the `transcribed.xlsx` file.
5. As soon as you make your first edit, all changes will be saved into a new file called `transcribed__edited__CURRENT_DATE_TIME.xlsx`
    - For the current session, all changes will be saved here. 
6. If you stop editing at the end of the day, then on your next session simply load the last `transcribed__edited__CURRENT_DATE_TIME.xlsx`file and start editing
    - VVE creates a new `__edited__` for each session for redundancy purposes
7. If you stopped part way through a previous project, you can click `skip to last viewed image` to jump ahead