# VoucherVisionEditor

[![VoucherVisionEditor](https://LeafMachine.org/img/LM2_Desktop_Narrow2.jpg "VoucherVisionEditor")](https://LeafMachine.org/)

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
      * [Installing Packages](#installing-packages-1)

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
[VoucherVision Demo](https://vouchervision.azurewebsites.net/)

---

# Installing VoucherVisionEditor

## Prerequisites
- Python 3.8 or later 

## Installation - Cloning the VoucherVisionEditor Repository
1. First, install Python 3.8.10, or greater, on your machine of choice. We have validated up to Python 3.11.
    - Make sure that you can use `pip` to install packages on your machine, or at least inside of a virtual environment.
    - Simply type `pip` into your terminal or PowerShell. If you see a list of options, you are all set. Otherwise, see
    either this [PIP Documentation](https://pip.pypa.io/en/stable/installation/) or [this help page](https://www.geeksforgeeks.org/how-to-install-pip-on-windows/)
2. Open a terminal window and `cd` into the directory where you want to install VoucherVisionEditor.
3. Clone the VoucherVisionEditor repository from GitHub by running `git clone https://github.com/Gene-Weaver/VoucherVisionEditor.git` in the terminal.
4. Move into the VoucherVisionEditor directory by running `cd VoucherVisionEditor` in the terminal.
5. To run VoucherVisionEditor we need to install its dependencies inside of a python virtual environmnet. Follow the instructions below for your operating system. 

## About Python Virtual Environments
A virtual environment is a tool to keep the dependencies required by different projects in separate places, by creating isolated python virtual environments for them. This avoids any conflicts between the packages that you have installed for different projects. It makes it easier to maintain different versions of packages for different projects.

For more information about virtual environments, please see [Creation of virtual environments](https://docs.python.org/3/library/venv.html)

---

## Installation - Ubuntu 20.04

### Virtual Environment

1. Still inside the VoucherVisionEditor directory, show that a venv is currently not active 
    <pre><code class="language-python">which python</code></pre>
    <button class="btn" data-clipboard-target="#code-snippet"></button>
2. Then create the virtual environment (venv_VVE is the name of our new virtual environment)  
    <pre><code class="language-python">python3 -m venv venv_VVE</code></pre>
    <button class="btn" data-clipboard-target="#code-snippet"></button>
3. Activate the virtual environment  
    <pre><code class="language-python">source ./venv_VVE/bin/activate</code></pre>
    <button class="btn" data-clipboard-target="#code-snippet"></button>
4. Confirm that the venv is active (should be different from step 1)  
    <pre><code class="language-python">which python</code></pre>
    <button class="btn" data-clipboard-target="#code-snippet"></button>
5. If you want to exit the venv, deactivate the venv using  
    <pre><code class="language-python">deactivate</code></pre>
    <button class="btn" data-clipboard-target="#code-snippet"></button>

### Installing Packages

1. Install the required libraries to use VoucherVisionEditor 
    <pre><code class="language-python">pip install streamlit pandas openpyxl Pillow</code></pre>
    <button class="btn" data-clipboard-target="#code-snippet"></button>

---

## Installation - Windows 10+

### Virtual Environment

1. Still inside the VoucherVisionEditor directory, show that a venv is currently not active 
    <pre><code class="language-python">python --version</code></pre>
    <button class="btn" data-clipboard-target="#code-snippet"></button>
2. Then create the virtual environment (venv_VVE is the name of our new virtual environment)  
    <pre><code class="language-python">python3 -m venv venv_VVE</code></pre>
    <button class="btn" data-clipboard-target="#code-snippet"></button>
3. Activate the virtual environment  
    <pre><code class="language-python">.\venv_VVE\Scripts\activate</code></pre>
    <button class="btn" data-clipboard-target="#code-snippet"></button>
4. Confirm that the venv is active (should be different from step 1)  
    <pre><code class="language-python">python --version</code></pre>
    <button class="btn" data-clipboard-target="#code-snippet"></button>
5. If you want to exit the venv, deactivate the venv using  
    <pre><code class="language-python">deactivate</code></pre>
    <button class="btn" data-clipboard-target="#code-snippet"></button>

### Installing Packages

1. Install the required dependencies to use VoucherVisionEditor  
    <pre><code class="language-python">pip install streamlit pandas openpyxl Pillow</code></pre>
    <button class="btn" data-clipboard-target="#code-snippet"></button>

---

# Running VoucherVisionEditor

1. In the terminal, move into the VoucherVisionEditor directory.
2. Make sure that your local version is updated by running `git pull` (you might need to use the Git Bash terminal).
3. We will launch VVE from the terminal. There are two primary flags for the launch command.
---
`--save-dir` defines where the edited file will be saved. VVE never overwrites the original transcription file. This must be the full file path to where 
the edited transcription.xlsx should be saved. If you need to pause an editing run and resume it at a later time, then the last "edited" file becomes the new input file, but `--save-dir` can remain the same because it will simply increment after each saved 

---
`--base-path` reroutes the file paths in the original transcription file is the files have been moved. The original transcription file saves the fill paths to the transcription JSON files, cropped labels images, and the original full specimen images. If the computerwhere VVE is running has access to these files and those file locations have not changed, then the `--base-path` option is not needed. But in the even that the original file paths are broken, this will rebuild the file paths to the new locations. 
### Example:
Say that you process images with VoucherVision and the output files are saved to `C:/user/documents/Project_1/Run_1`. The folder `Run_1` contains the main output directories, including the `Original_Images` and `Transcription` folders. To make the output portable, we would copy and move everything inside of the `Project_1` folder. Now the new location might be something like `E:/usr/home/Project_1/Run_1`. So for the `--base=path` option we would include eveerything in the new file path up to the `Transcription` like this:
`--base-path E:/usr/home/Project_1/Run_1`
<pre><code class="language-python">python3 LeafMachine2.py</code></pre>
<button class="btn" data-clipboard-target="#code-snippet"></button>