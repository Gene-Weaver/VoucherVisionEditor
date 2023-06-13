# VoucherVisionEditor

[![VoucherVision](https://LeafMachine.org/img/LM2_Desktop_Narrow2.jpg "VoucherVision")](https://LeafMachine.org/)

Table of Contents
=================

* [Table of Contents](#table-of-contents)
* [Installing VoucherVision](#installing-VoucherVision)
   * [Prerequisites](#prerequisites)
   * [Installation - Cloning the VoucherVision Repository](#installation---cloning-the-VoucherVision-repository)
   * [About Python Virtual Environments](#about-python-virtual-environments)
   * [Installation - Ubuntu 20.04](#installation---ubuntu-2004)
      * [Virtual Environment](#virtual-environment)
      * [Installing Packages](#installing-packages)
   * [Installation - Windows 10+](#installation---windows-10)
      * [Virtual Environment](#virtual-environment-1)
      * [Installing Packages](#installing-packages-1)



---

# Installing VoucherVision

## Prerequisites
- Python 3.8 or later 

## Installation - Cloning the VoucherVision Repository
1. First, install Python 3.8.10, or greater, on your machine of choice.
    - Make sure that you can use `pip` to install packages on your machine, or at least inside of a virtual environment.
    - Simply type `pip` into your terminal or PowerShell. If you see a list of options, you are all set. Otherwise, see
    either this [PIP Documentation](https://pip.pypa.io/en/stable/installation/) or [this help page](https://www.geeksforgeeks.org/how-to-install-pip-on-windows/)
2. Open a terminal window and `cd` into the directory where you want to install VoucherVision.
3. Clone the VoucherVision repository from GitHub by running `git clone https://github.com/Gene-Weaver/VoucherVisionEditor.git` in the terminal.
4. Move into the VoucherVision directory by running `cd VoucherVision` in the terminal.
5. To run VoucherVision we need to install its dependencies inside of a python virtual environmnet. Follow the instructions below for your operating system. 

## About Python Virtual Environments
A virtual environment is a tool to keep the dependencies required by different projects in separate places, by creating isolated python virtual environments for them. This avoids any conflicts between the packages that you have installed for different projects. It makes it easier to maintain different versions of packages for different projects.

For more information about virtual environments, please see [Creation of virtual environments](https://docs.python.org/3/library/venv.html)

---

## Installation - Ubuntu 20.04

### Virtual Environment

1. Still inside the VoucherVision directory, show that a venv is currently not active 
    <pre><code class="language-python">which python</code></pre>
    <button class="btn" data-clipboard-target="#code-snippet"></button>
2. Then create the virtual environment (venv_LM2 is the name of our new virtual environment)  
    <pre><code class="language-python">python3 -m venv venv_LM2</code></pre>
    <button class="btn" data-clipboard-target="#code-snippet"></button>
3. Activate the virtual environment  
    <pre><code class="language-python">source ./venv_LM2/bin/activate</code></pre>
    <button class="btn" data-clipboard-target="#code-snippet"></button>
4. Confirm that the venv is active (should be different from step 1)  
    <pre><code class="language-python">which python</code></pre>
    <button class="btn" data-clipboard-target="#code-snippet"></button>
5. If you want to exit the venv, deactivate the venv using  
    <pre><code class="language-python">deactivate</code></pre>
    <button class="btn" data-clipboard-target="#code-snippet"></button>

### Installing Packages

1. Install the required libraries to use VoucherVision 
    <pre><code class="language-python">pip install streamlit pandas openpyxl Pillow</code></pre>
    <button class="btn" data-clipboard-target="#code-snippet"></button>

---

## Installation - Windows 10+

### Virtual Environment

1. Still inside the VoucherVision directory, show that a venv is currently not active 
    <pre><code class="language-python">python --version</code></pre>
    <button class="btn" data-clipboard-target="#code-snippet"></button>
2. Then create the virtual environment (venv_LM2 is the name of our new virtual environment)  
    <pre><code class="language-python">python3 -m venv venv_LM2</code></pre>
    <button class="btn" data-clipboard-target="#code-snippet"></button>
3. Activate the virtual environment  
    <pre><code class="language-python">.\venv_LM2\Scripts\activate</code></pre>
    <button class="btn" data-clipboard-target="#code-snippet"></button>
4. Confirm that the venv is active (should be different from step 1)  
    <pre><code class="language-python">python --version</code></pre>
    <button class="btn" data-clipboard-target="#code-snippet"></button>
5. If you want to exit the venv, deactivate the venv using  
    <pre><code class="language-python">deactivate</code></pre>
    <button class="btn" data-clipboard-target="#code-snippet"></button>

### Installing Packages

1. Install the required dependencies to use VoucherVision  
    <pre><code class="language-python">pip install streamlit pandas openpyxl Pillow</code></pre>
    <button class="btn" data-clipboard-target="#code-snippet"></button>

---