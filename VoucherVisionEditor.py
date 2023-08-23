import streamlit as st
import pandas as pd
import json, os, argparse, shutil, re, toml
import subprocess
import threading
from PIL import Image
from utils import *
import webbrowser
import base64
from io import BytesIO

# pip install streamlit pandas Pillow openpyxl streamlit-aggrid
# Windows
# streamlit run your_script.py -- --SAVE_DIR /path/to/save/dir
# Linux
# export SAVE_DIR=/path/to/save/dir && streamlit run your_script.py


### To run:
# streamlit run VoucherVisionEditor.py -- 
# --base-path D:/Dropbox/LM2_Env/VoucherVision_Datasets/POC_chatGPT__2022_09_07_thru12_S3_jacortez_AllAsia/2022_09_07_thru12_S3_jacortez_AllAsia_2023_06_16__02-12-26
# --save-dir D:/D_Desktop/OUT
os.chdir(os.path.dirname(os.path.realpath(__file__)))
st.set_page_config(layout="wide", page_icon='img/icon.ico', page_title='VoucherVision Editor')


# Initialize Streamlit Session State if it hasn't been initialized yet
if "row_to_edit" not in st.session_state:
    st.session_state.row_to_edit = 0

if 'data' not in st.session_state:
    st.session_state.data = None

if "file_name" not in st.session_state:
    st.session_state.file_name = None

if "user_input" not in st.session_state:
    st.session_state.user_input = {}

if "clear_count" not in st.session_state:
    st.session_state.clear_count = 0

if "track_edits" not in st.session_state:
    st.session_state.track_edits = []

if "current_options" not in st.session_state:
    st.session_state.setdefault('current_options', [] if st.session_state.track_edits else [])

if "progress_counter" not in st.session_state:
    st.session_state.progress_counter = 0

if "progress_counter_overall" not in st.session_state:
    st.session_state.progress_counter_overall = 0

if "progress" not in st.session_state:
    st.session_state.progress = 0

if "progress_index" not in st.session_state:
    st.session_state.progress_index = 0

if "access_option" not in st.session_state:
    st.session_state.access_option = 'Labeler'

# Store the previous value of st.session_state.access_option
if 'previous_access_option' not in st.session_state:
    st.session_state.previous_access_option = 'Labeler'

if 'image_option' not in st.session_state:
    st.session_state.image_option = 'Original'

if 'default_to_original' not in st.session_state:
    st.session_state.default_to_original = True

if 'view_option' not in st.session_state:
    st.session_state.view_option = "Form View"

if 'show_helper_text' not in st.session_state:
    st.session_state.show_helper_text = False

if 'set_image_size' not in st.session_state:
    st.session_state.set_image_size = 'Medium'

if 'set_image_size_previous' not in st.session_state:
    st.session_state.set_image_size_previous = 'Medium'

if 'set_image_size_px' not in st.session_state:
    st.session_state.set_image_size_px = 1100

if 'set_image_size_pxh' not in st.session_state:
    st.session_state.set_image_size_pxh = 80

if 'image_fill' not in st.session_state:
    st.session_state.image_fill = "More"

if 'use_extra_image_options' not in st.session_state:
    st.session_state.use_extra_image_options = False

if 'is_fitted_image' not in st.session_state:
    st.session_state.is_fitted_image = False

if 'fitted_image_width' not in st.session_state:
    st.session_state.fitted_image_width = 600

parser = argparse.ArgumentParser(description='Define save location of edited file.')

# Add parser argument for save directory
parser.add_argument('--save-dir', type=str, default=None,
                    help='Directory to save output files')
parser.add_argument('--base-path', type=str, default='',
                    help='New base path to replace the existing one, up to "/Transcription"')

# Parse the arguments
try:
    args = parser.parse_args()
except SystemExit as e:
    # This exception will be raised if --help or invalid command line arguments
    # are used. Currently streamlit prevents the program from exiting normally
    # so we have to do a hard exit.
    os._exit(e.code)

###############################################################
#################          Config          ####################
###############################################################
def setup_streamlit_config(mapbox_key=''):
    # Define the directory path and filename
    dir_path = ".streamlit"
    file_path = os.path.join(dir_path, "config.toml")

    # Check if directory exists, if not create it
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)

    # If the mapbox_key is empty, and the config file already has a mapbox key, don't overwrite the file
    if mapbox_key == '':
        if os.path.exists(file_path):
            config_data = toml.load(file_path)
            existing_key = config_data.get('mapbox', {}).get('token', None)
            if existing_key is not None and existing_key != '':
                return
    
    # Create or modify the file with the provided content
    config_content = f"""
    [theme]
    base = "dark"
    primaryColor = "#00ff00"

    [server]
    enableStaticServing = true
    runOnSave = true
    port = 8523
    """

    if mapbox_key != '':
        config_content += f"""
        [mapbox]
        token = "{mapbox_key}"
        """

    with open(file_path, "w") as f:
        f.write(config_content.strip())

###############################################################
#################       Definitions        ####################
###############################################################
color_map = {
    "TAXONOMY": 'blue', 
    "GEOGRAPHY": 'orange', 
    "LOCALITY": 'green',
    "COLLECTING": 'violet', 
    "MISCELLANEOUS": 'red', 
    "OCR": '#7fbfff', 
}

color_map_json = {
    "TAXONOMY": "#7fbfff", # pastel blue
    "GEOGRAPHY": "#f6a14f",  # pastel orange
    "LOCALITY": "#48ca48", # pastel green
    "COLLECTING": "#bf7fbf",  # pastel purple
    "MISCELLANEOUS": "#ff3333",  # pastel red
}

grouping = {
    "TAXONOMY": ["Catalog Number", "Genus", "Species", "subspecies", "variety", "forma",],
    "GEOGRAPHY": ["Country", "State", "County", "Verbatim Coordinates",],
    "LOCALITY": ["Locality Name", "Min Elevation", "Max Elevation", "Elevation Units",],
    "COLLECTING": ["Datum","Cultivated","Habitat","Collectors","Collector Number", "Verbatim Date","Date", "End Date",],
}


###############################################################
#################          Utils           ####################
###############################################################
def prompt_for_mapbox_key():
    # Define the directory path and filename
    dir_path = ".streamlit"
    file_path = os.path.join(dir_path, "config.toml")

    # Check if directory exists, if not create it
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)

    # If config file exists, load existing Mapbox key, if any
    existing_key = None
    if os.path.exists(file_path):
        config_data = toml.load(file_path)
        existing_key = config_data.get('mapbox', {}).get('token', None)

    # Ask the user for their Mapbox key (pre-fill with existing key if available)
    st.markdown("""#### Mapbox Key""")
    st.markdown("""VVE will display the location of valid GPS coordinates on a map to aid with review. We use the Mapbox API for this service. Providing no key will rely on the free
    public API, which may meet your needs. If maps no longer display, or if you have a Mapbox key, then enter it below. The key will only be stored locally on your device in the `VoucherVisionEditor/.streamlit/config.toml` file. These files are created on first startup.""")
    st.markdown("""You may update the key at any time. To remove an existing key, delete the `config.toml` file.""")

    if existing_key is not None and existing_key != '':
        st.info("Mapbox key present in the /.streamlit/config.toml file!")
    
    mapbox_key = st.text_input('Enter your Mapbox key here:', '')

    return mapbox_key

# Function to convert image to base64
def image_to_base64(img):
    buffered = BytesIO()
    img.save(buffered, format="JPEG")
    return base64.b64encode(buffered.getvalue()).decode()


# Use SAVE_DIR where needed
def save_data():
    # Check the file extension and save to the appropriate format
    if st.session_state.file_name.endswith('.csv'):
        file_path = os.path.join(st.session_state.SAVE_DIR, st.session_state.file_name)
        st.session_state.data.to_csv(file_path, index=False)
        st.success('Saved (CSV)')
        print(f"Saved (CSV) {file_path}")
    elif st.session_state.file_name.endswith('.xlsx'):
        file_path = os.path.join(st.session_state.SAVE_DIR, st.session_state.file_name)
        st.session_state.data.to_excel(file_path, index=False)
        st.success('Saved (XLSX)')
        print(f"Saved (XLSX) {file_path}")
    else:
        st.error('Unknown file format.')

def load_data(mapbox_key):
    if 'data' not in st.session_state or st.session_state.data is None:
        uploaded_file = st.file_uploader("Choose a CSV or Excel file", type=["csv", "xlsx"])
    else:
        uploaded_file = None

    if uploaded_file is not None:
        setup_streamlit_config(mapbox_key)

        if uploaded_file.type == "text/csv":
            data = pd.read_csv(uploaded_file, dtype=str)
        elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":
            data = pd.read_excel(uploaded_file, dtype=str)

        if "track_view" not in data.columns:
            data["track_view"] = 'False'
        if 'track_edit' not in data.columns:
            data["track_edit"] = ["" for _ in range(len(data))]

        st.session_state.data = data.fillna('')
        file_extension = "csv" if uploaded_file.type == "text/csv" else "xlsx"
        st.session_state.file_name = f"{uploaded_file.name.split('.')[0]}_edited.{file_extension}"

        # If BASE_PATH is provided, replace old base paths in the dataframe
        if st.session_state.BASE_PATH != '':
            st.session_state.data['path_to_crop'] = st.session_state.data['path_to_crop'].apply(lambda old_path: replace_base_path(old_path, st.session_state.BASE_PATH, 'crop'))
            st.session_state.data['path_to_original'] = st.session_state.data['path_to_original'].apply(lambda old_path: replace_base_path(old_path, st.session_state.BASE_PATH, 'original'))
            st.session_state.data['path_to_helper'] = st.session_state.data['path_to_helper'].apply(lambda old_path: replace_base_path(old_path, st.session_state.BASE_PATH, 'json'))
            st.session_state.data['path_to_content'] = st.session_state.data['path_to_content'].apply(lambda old_path: replace_base_path(old_path, st.session_state.BASE_PATH, 'json'))
        
        # Determine SAVE_DIR from the 'path_to_content' column
        first_path_to_content = st.session_state.data['path_to_content'][0]
        print("")
        print(first_path_to_content)
        print("")
        parts = first_path_to_content.split(os.path.sep)
        transcription_index = parts.index('Transcription') if 'Transcription' in parts else None
        print("")
        print(parts)
        print("")
        if transcription_index is not None:
            # add a slash after the drive letter if it is missing
            if len(parts[0]) == 2 and parts[0][1] == ":":
                parts[0] += os.path.sep
            st.session_state.SAVE_DIR = os.path.join(*parts[:transcription_index+1])
            print(f"Saving edited file to {st.session_state.SAVE_DIR}")
            if not os.path.exists(st.session_state.SAVE_DIR):
                print("UH OH! new dir created but it should not be")
                os.makedirs(st.session_state.SAVE_DIR)


def start_server():
    current_dir = os.path.dirname(os.path.abspath(__file__))
        # Create the path to the new 'static' directory
    static_folder_path = os.path.join(current_dir, 'static')
        # Create 'static' directory
    os.makedirs(static_folder_path, exist_ok=True)
    # Ensure the server is run in a separate thread so it doesn't block the Streamlit app
    def target():
        subprocess.run(["python", "-m", "http.server"], cwd=static_folder_path, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    threading.Thread(target=target).start()

    # Get the directory of the current file 
    st.session_state.current_dir = os.path.dirname(os.path.abspath(__file__))
    # Create the path to the new 'static' directory
    st.session_state.static_folder_path = os.path.join(st.session_state.current_dir, 'static')
    # Create 'static' directory
    os.makedirs(st.session_state.static_folder_path, exist_ok=True)
    st.session_state.static_folder_path_o = os.path.join(st.session_state.static_folder_path, "static_og")
    st.session_state.static_folder_path_c = os.path.join(st.session_state.static_folder_path, "static_cr")
    os.makedirs(st.session_state.static_folder_path_o, exist_ok=True)
    os.makedirs(st.session_state.static_folder_path_c, exist_ok=True)

    logo_path = os.path.join(st.session_state.static_folder_path_c, 'logo.png')
    shutil.copy("img/logo.png", logo_path)

    relative_path_to_logo = os.path.relpath(logo_path, st.session_state.current_dir).replace('\\', '/')
    split_path = relative_path_to_logo.split('/')
    relative_path_to_logo = os.path.sep.join(split_path[1:])
    st.session_state.logo_path = relative_path_to_logo.replace('\\', '/')

def do_rerun():
    st.experimental_rerun()

def clear_directory():
    st.session_state.clear_count += 1
    if st.session_state.clear_count == 1:
        print("All Zoom files from previous session have been deleted")
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # Create the path to the new 'static' directory
        static_folder_path = os.path.join(current_dir, 'static')
        # Create 'static' directory
        os.makedirs(static_folder_path, exist_ok=True)
        for root, dirs, files in os.walk(static_folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    if os.path.isfile(file_path) or os.path.islink(file_path):
                        os.unlink(file_path)  # remove file or symbolic link
                except Exception as e:
                    print(f'Failed to delete {file_path}. Reason: {e}')


def get_directory_paths(args):
    save_dir_help = """
    Defines where the edited file will be saved. 
    VVE never overwrites the original transcription file. 
    This must be the full file path to where the edited transcription.xlsx should be saved. 
    If you need to pause an editing run and resume it at a later time, 
    then the last "edited" file becomes the new input file, 
    but --save-dir can remain the same because it will simply increment after each session.
    """
    
    base_path_help = """
    Reroutes the file paths in the original transcription file if the files have been moved. 
    The original transcription file saves the full paths to the transcription JSON files, 
    cropped labels images, and the original full specimen images. 
    If the computer where VVE is running has access to these files and those file locations have not changed, 
    then the --base-path option is not needed. 
    But in the event that the original file paths are broken, this will rebuild the file paths to the new locations.
    
    For example, if the old path in your file is: 'C:/Users/old_user/Documents/Project/Transcription/File.json'
    
    and the new base path you enter is: 'D:/New_Project_Location/'
    
    then the new path for the file will become: 'D:/New_Project_Location/Transcription/File.json'.
    """
    bp_text = '''
    #### Save Directory and Base Path Configuration
    When launching the VoucherVision Editor (VVE) from the command line, two optional arguments can be specified: `--save-dir` and `--base-path`. 

    - `--save-dir` defines where the edited file will be saved. VVE never overwrites the original transcription file. This must be the full file path to where the edited transcription.xlsx should be saved. If you need to pause an editing run and resume it at a later time, then the last "edited" file becomes the new input file, but `--save-dir` can remain the same because it will simply increment after each save.

    - `--base-path` optional. Reroutes the file paths in the original transcription file ***if the files have been moved***. The original transcription file saves the full paths to the transcription JSON files, cropped labels images, and the original full specimen images. If the computer where VVE is running has access to these files and those file locations have not changed, then the `--base-path` option is not needed. But in the event that the original file paths are broken, this will rebuild the file paths to the new locations.

    If `--save-dir` and `--base-path` are not provided in the command line arguments, you can specify them below.
    '''
    st.markdown(bp_text)

    # Get the save directory and base path from the parsed arguments or use the Streamlit input
    st.markdown("""#### Save Directory""")
    st.session_state.SAVE_DIR = args.save_dir if args.save_dir else st.text_input('Enter the directory to save output files', help=save_dir_help)
    st.markdown("""#### Base Path""")
    st.session_state.BASE_PATH = args.base_path if args.base_path else st.text_input('Include the full path to the folder that contains "/Transcription", but do not include "/Transcription" in the path', help=base_path_help)

              

def add_default_option_if_not_present():
    # Add default option if "track_edit" is empty and doesn't contain the default option already
    if group_options[0] not in st.session_state.data.loc[st.session_state.row_to_edit, "track_edit"].split(","):
        if st.session_state.data.loc[st.session_state.row_to_edit, "track_edit"]:
            st.session_state.data.loc[st.session_state.row_to_edit, "track_edit"] += "," + group_options[0]
        else:
            st.session_state.data.loc[st.session_state.row_to_edit, "track_edit"] = group_options[0]

###############################################################
#################      Progress Bars       ####################
###############################################################
def update_progress_bar():
    # Split the "track_edit" field into a list of options
    current_options = st.session_state.data.loc[st.session_state.row_to_edit, "track_edit"].split(",")

    # Count how many of the options are in group_options
    pg = len([option for option in current_options if option in group_options])

    # Update the progress counter
    if pg > st.session_state.progress_counter:
        st.session_state.progress_counter = pg

    # Calculate the progress as a fraction of the total number of options
    progress_fraction = min(pg / len(group_options), 1.0)

    # Display the progress bar with text
    st.progress(progress_fraction)
    # st.write(f"{int(st.session_state.progress_counter)}/{len(group_options)} Groups")
    st.session_state.progress = pg
    # print(f"PG{pg}")

def update_progress_bar_overall():
    # Get the index of the last True value in "track_view"
    last_true_index = st.session_state.data[st.session_state.data["track_view"] == 'True'].index.max()

    # Get total number of rows
    total_rows = len(st.session_state.data)

    # Find the last row where "track_edit" has all group options
    last_full_view_index = st.session_state.data[st.session_state.data["track_edit"].apply(lambda x: set(group_options).issubset(set(x.split(','))))].index.max()
    # Handle NaN last_full_view_index
    if pd.isnull(last_full_view_index):
        last_full_view_index = 0

    # Calculate the progress_overall as a fraction
    progress_overall_fraction = min(last_full_view_index / total_rows, 1.0)
    print(progress_overall_fraction)
    # Display the progress_overall information
    # st.write(f"When 'Admin' is enabled, the following progress metrics will not update, but edits can still  be made.")
    st.progress(progress_overall_fraction)
    # st.write(f"Last viewed image: {last_true_index} -- Last completed image: {last_full_view_index}")
    st.write(f"Viewed *{last_true_index}* of *{total_rows}* images")
    st.write(f"Completed *{last_full_view_index}* of *{total_rows}* images")
    # Display the progress bar with text
    return last_true_index, last_full_view_index



###############################################################
########################## Layouts ############################
###############################################################
def layout_image_proportion():
    """
    Set layout columns based on st.session_state.image_fill.
    
    Returns:
        tuple: (c_left, c_right) - The two columns created based on the image_fill state.
    """
    if st.session_state.image_fill == "Maximum":
        c_left, c_right = st.columns([5, 13])
    elif st.session_state.image_fill == "More":
        c_left, c_right = st.columns([6, 12])
    else:
        c_left, c_right = st.columns([8, 8])
    
    return c_left, c_right

def show_header_welcome():
    # Create three columns
    h1, h2, h3 = st.columns([2,1,2])
    # Use the second (middle) column for the logo
    with h2:
        # st.image("img/logo.png", use_column_width=True)
        st.markdown(f'<a href="https://github.com/Gene-Weaver/VoucherVisionEditor"><img src="http://localhost:8000/{st.session_state.logo_path}" width="200"></a>', unsafe_allow_html=True)
        hide_img_fs = '''
        <style>
        button[title="View fullscreen"]{
            visibility: hidden;}
        </style>
        '''
        st.markdown(hide_img_fs, unsafe_allow_html=True)

def show_header_main():
    with st.sidebar:
        # Logo and Title
        h1, h2, h3 = st.columns([1,6,1])
        with h2:
            st.image(f"http://localhost:8000/{st.session_state.logo_path}", use_column_width=True)
            st.markdown("<h1 style='text-align: center;'>VoucherVision Editor</h1>", unsafe_allow_html=True)
            # Use the first column for the logo and the second for the title
            # st.image("img/logo.png", width=200)  # adjust width as needed
            # st.markdown(f'<a href="https://github.com/Gene-Weaver/VoucherVisionEditor"><img src="http://localhost:8000/{st.session_state.logo_path}" width="100"></a>', unsafe_allow_html=True)
        
        # Image Layout Focus selectbox
        st.session_state.image_fill = st.sidebar.selectbox("Image Layout Focus", ["More", "Maximum", "Balanced"])
        
        # Image Size selectbox
        st.session_state.set_image_size = st.sidebar.selectbox("Image Size", ["Medium", "Large", "Small", "Custom", "Auto Width", "Fitted"])

        # Set Image Width slider
        if st.session_state.set_image_size == "Custom":
            image_sizes = list(range(200, 2601, 100))
            st.session_state.set_image_size_px = st.select_slider('Set Image Width', options=image_sizes, value=1500)

        # Set Viewing Height slider
        if st.session_state.set_image_size != "Auto Width":
            image_sizes = list(range(20, 201, 5))
            st.session_state.set_image_size_pxh = st.select_slider('Set Viewing Height', options=image_sizes, value=80)

        # Access selectbox
        st.session_state.access_option = st.sidebar.selectbox("Access", ["Labeler", "Admin"])

        # Choose a View selectbox
        st.session_state.view_option = st.sidebar.selectbox("Choose a View", ["Form View", "Data Editor"], disabled=True)

        # Store previous image size
        st.session_state.set_image_size_previous = st.session_state.set_image_size

        ######## Additional Options ################
        st.sidebar.header('Options') #,help='Visible as Admin')
        
        st.session_state.use_extra_image_options = st.sidebar.checkbox("Include toggle for fitted image view.", value=False)
        if st.session_state.use_extra_image_options:
            image_sizes_fitted = list(range(100, 1201, 50))
            st.session_state.set_image_size_px = st.select_slider(
                'Set Fitted Image Width',
                options=image_sizes_fitted,value=600)
        
        # fitted_image_width
        st.session_state.default_to_original = st.sidebar.checkbox("Default to full image each time 'Next' or 'Previous' is pressed.", value=True)  


###############################################################
###################### Load Files #############################
###############################################################
def load_json_helper_files():
    """
    Load related JSON files based on the current row being edited. 
    Updates the st.session_state with 'json_dict' for the helper JSON and 'OCR_JSON' for the OCR data.
    """
    if st.session_state['last_row_to_edit'] != st.session_state.row_to_edit:
        JSON_path = st.session_state.data.loc[st.session_state.row_to_edit, "path_to_helper"]

        if JSON_path:
            with open(JSON_path, "r") as file:
                st.session_state['json_dict'] = json.load(file)

        # Load second JSON (OCR)
        original_JSON_path = st.session_state.data.loc[st.session_state.row_to_edit, "path_to_helper"]
        
        if original_JSON_path:
            # Breakdown the path into parts
            path_parts = original_JSON_path.split(os.path.sep)
            
            # Change the last directory name to 'Individual_OCR'
            path_parts[-2] = 'Individual_OCR'
            
            # Combine the parts back together
            OCR_JSON_path = os.path.sep.join(path_parts)
            
            # Check if the file exists
            if os.path.isfile(OCR_JSON_path):
                with open(OCR_JSON_path, "r") as file:
                    st.session_state['OCR_JSON'] = json.load(file)


###############################################################
####################### Button Press ##########################
###############################################################
def on_press_previous():
    """
    Handle actions when the "Previous" button is pressed.
    """
    if st.button("Previous", use_container_width=True):
        st.session_state.progress_counter = 0
        if st.session_state.current_options:
            # Store current options as a list in "track_edit" column
            st.session_state.data.loc[st.session_state.row_to_edit, "track_edit"] = st.session_state.current_options
        # Add default option if "track_edit" is empty and doesn't contain the default option already
        add_default_option_if_not_present()

        if st.session_state.row_to_edit == st.session_state.data.index[0]:
            if st.session_state.access_option == 'Admin':
                st.session_state.row_to_edit = st.session_state.data.index[-1]
        else:
            st.session_state.row_to_edit -= 1

        # st.session_state["group_option"] = group_options[0]  # Reset the group_option
        if st.session_state.default_to_original:
            st.session_state.image_option = 'Original'
        st.experimental_rerun()

def on_press_next(group_options):
    """
    Handle actions when the "Next" button is pressed.
    """
    if st.session_state.progress == len(group_options) or st.session_state.access_option == 'Admin':
        if st.button("Next", type="primary", use_container_width=True):
            st.session_state.progress_counter = 0
            st.session_state.progress_index = 0
            if st.session_state.current_options:
                # Store current options as a list in "track_edit" column
                st.session_state.data.loc[st.session_state.row_to_edit, "track_edit"] = st.session_state.current_options
            # Add default option if "track_edit" is empty and doesn't contain the default option already
            add_default_option_if_not_present()

            if st.session_state.row_to_edit == st.session_state.data.index[-1]:
                st.session_state.row_to_edit = st.session_state.data.index[0]
            else:
                st.session_state.row_to_edit += 1

            st.session_state["group_option"] = group_options[0]  # Reset the group_option
            if st.session_state.default_to_original:
                st.session_state.image_option = 'Original'
            st.experimental_rerun()
    else:
        st.info("Please confirm all categories.")

def on_press_skip_to_bookmark():
    if st.button('Skip to last viewed image',key=f"Skip_to_last_viewed2", use_container_width=True):
        last_true_index, last_fully_viewed = update_progress_bar_overall()
        st.session_state.row_to_edit = int(last_true_index)
        st.experimental_rerun()

def on_press_confirm_content():
    if st.button('Confirm Content',key=f"Confirm_Content1", use_container_width=True, type="primary"):
        st.session_state.progress_index += 1
        for i, option in enumerate(group_options):
            if i == st.session_state.progress_index:
                # group_option_cols[i].button(option, use_container_width=True, disabled=do_disable_btn)
                
                st.session_state["group_option"] = option
                group_option = option

                if "track_edit" not in st.session_state.data.columns:
                    st.session_state.data["track_edit"] = [[group_options[0]] if group_options[0] else [] for _ in range(len(st.session_state.data))]

                if st.session_state.access_option != 'Admin': 
                    if option not in st.session_state.data.loc[st.session_state.row_to_edit, "track_edit"].split(","):
                        current_edit_track = st.session_state.data.loc[st.session_state.row_to_edit, "track_edit"]
                        if current_edit_track:
                            new_edit_track = current_edit_track + "," + option
                        else:
                            new_edit_track = option
                        st.session_state.data.loc[st.session_state.row_to_edit, "track_edit"] = new_edit_track

                        add_default_option_if_not_present()
        with c_form:
            save_data()
        con_form.empty()
        st.experimental_rerun()


###############################################################
################# Display Rows in the Form ####################
###############################################################
def form_layout(group_option, grouping, color_map):
    """
    Display form layout based on group_option and update st.session_state.data.

    Parameters:
        group_option (str): Current group option.
        grouping (dict): Dictionary mapping groups to fields.
        color_map (dict): Dictionary mapping groups to colors.
    """
    columns_to_show = st.session_state.data.columns if group_option == "ALL" else grouping[group_option]
    for col in columns_to_show:
        if col not in ['track_view', 'track_edit']:
            # Find the corresponding group and color
            unique_key = f"{st.session_state.row_to_edit}_{col}"
            for group, fields in grouping.items():
                if col in fields:
                    color = color_map.get(group, "#FFFFFF")  # default to white color
                    break
            else:
                color = color_map.get("MISCELLANEOUS", "#FFFFFF")  # default to white color

            colored_label = f":{color}[{col}]"

            # IF admin, allow barcode to be edited
            if (st.session_state.access_option == 'Admin' and (col == 'Catalog Number')): 
                # Show editable catalog number to admin
                st.session_state.user_input[col] = st.text_input(colored_label, st.session_state.data.loc[st.session_state.row_to_edit, col], key=unique_key,)
            elif (st.session_state.access_option == 'Labeler' and (col == 'Catalog Number')): 
                # Show disabled catalog number to labeler
                st.session_state.user_input[col] = st.text_input(colored_label, st.session_state.data.loc[st.session_state.row_to_edit, col], key=unique_key, disabled=True)
            else:
                st.session_state.user_input[col] = st.text_input(colored_label, st.session_state.data.loc[st.session_state.row_to_edit, col], key=unique_key)

            if st.session_state.user_input[col] != st.session_state.data.loc[st.session_state.row_to_edit, col]:
                st.session_state.data.loc[st.session_state.row_to_edit, col] = st.session_state.user_input[col]
                save_data()


###############################################################
################# Display JSON Helper Text ####################
###############################################################
def display_json_helper_text():
    # Check for presence of 'json_dict' in session state
    if 'json_dict' in st.session_state:
        # Button to toggle extra helper text
        form_pre_text = st.empty()
        with form_pre_text.container():
            on_press_show_helper_text()
        
        # Display helper text if toggled on
        if st.session_state.show_helper_text:
            json_dict = st.session_state['json_dict']
            
            # Load OCR_JSON if available
            if 'OCR_JSON' in st.session_state:
                OCR_JSON = st.session_state['OCR_JSON']

            # Create tabs
            con_tabs = st.empty()
            with con_tabs.container():
                tab1, tab2, tab3 = st.tabs([group_option, "Misc", "OCR"])

                # Iterate through main keys and values in json_dict
                for main_key, main_value in json_dict.items():
                    if group_option == 'ALL':
                        display_tab_content(tab1, main_key, main_value, color_map_json)
                        if main_key == 'MISCELLANEOUS':
                            display_tab_content(tab2, main_key, main_value, color_map_json)
                    elif main_key == 'MISCELLANEOUS':
                        display_tab_content(tab2, main_key, main_value, color_map_json)
                    elif ((main_key == group_option) and (main_key != 'MISCELLANEOUS')):
                        display_tab_content(tab1, main_key, main_value, color_map_json)

                # Display All OCR Text in tab3
                with tab3:
                    color = color_map.get('OCR', "#FFFFFF") 
                    st.markdown(f"<h4 style='color: {color};'>All OCR Text</h4><br>", unsafe_allow_html=True)
                    cleaned_OCR_text = remove_number_lines(OCR_JSON['OCR'])
                    OCR_show = cleaned_OCR_text.replace('\n', '<br/>')
                    st.markdown(f"""<p style='font-size:20px;'>{OCR_show}</p><br>""", unsafe_allow_html=True)

def display_tab_content(tab, main_key, main_value, color_map_json):
    """
    Display content for a specific tab.
    """
    with tab:
        color = color_map_json.get(main_key, "black")  # Default to black if key is not in color_map
        st.markdown(f"<h4 style='color: {color};'>{main_key}</h4><br>", unsafe_allow_html=True)
        
        if isinstance(main_value, dict):
            for sub_key, sub_value in main_value.items():
                if sub_value:
                    sub_value_show = remove_number_lines(sub_value)
                    sub_value_show = sub_value_show.replace('\n', '<br/>')
                    st.markdown(f"<b style='font-size:20px;'>{sub_key}: <br></b> {sub_value_show}<br>", unsafe_allow_html=True)

def on_press_show_helper_text():
    if st.button('Show Predicted Text',key=f"Show_help2", use_container_width=True, type="secondary"):
        if st.session_state.show_helper_text == True:
            st.session_state.show_helper_text = False
        elif st.session_state.show_helper_text == False:
            st.session_state.show_helper_text = True
        st.experimental_rerun()


###############################################################
###################### Validate Fields ########################
###############################################################
def validate_verbatim_coordinates():
    verbatim_coordinates = st.session_state.data.loc[st.session_state.row_to_edit, 'Verbatim Coordinates']
    if verbatim_coordinates:
        try:
            do_warn = check_for_sep(verbatim_coordinates)
            if do_warn:
                st.warning("Possibly invalid GPS coordinates! Lacks separator , - | ")

            # Split latitude and longitude from the verbatim_coordinates using regex
            verbatim_coordinates = verbatim_coordinates.strip()
            coords = re.split(',|-\s', verbatim_coordinates)
            # print(len(coords))
            # Check if we have two separate coordinates
            if len(coords) != 2:
                st.warning("Possibly invalid GPS coordinates! Exactly two coordinate values not found.")
            
            lat, lon = coords

            # Parse the coordinates
            lat, lon = parse_coordinate(lat.strip()), parse_coordinate(lon.strip())

            # Check if the coordinates are within the valid ranges
            if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
                st.warning("Invalid GPS coordinates! Values are out of bounds.")
            else:
                # Create a dataframe with latitude and longitude
                map_data = pd.DataFrame({
                    'lat': [lat],
                    'lon': [lon]
                })

                # Create a map with the coordinates
                st.map(map_data, zoom=3)
        except ValueError:
            st.error("Invalid GPS coordinates!\nIncorrect OR unsupported coordinate format.")
            pass

###############################################################
###################### Image Handling #########################
###############################################################
def image_path_and_load():
    """
    Update the image path based on the current row being edited and the selected image option.
    Then, load the image into st.session_state.
    """
    # Check if the current row or image option has changed
    if (st.session_state['last_row_to_edit'] != st.session_state.row_to_edit or 
        'last_image_option' not in st.session_state or 
        st.session_state['last_image_option'] != st.session_state.image_option):

        # Update the image path based on the selected image option
        if st.session_state.image_option == 'Original':
            st.session_state['image_path'] = st.session_state.data.loc[st.session_state.row_to_edit, "path_to_original"]
        elif st.session_state.image_option == 'Cropped':
            st.session_state['image_path'] = st.session_state.data.loc[st.session_state.row_to_edit, "path_to_crop"]
        
        # Load the image if the image path is not null
        if pd.notnull(st.session_state['image_path']):
            new_img_path = st.session_state['image_path']
            new_img_path_fname = os.path.basename(new_img_path)
            print(f'LOADING IMAGE: {new_img_path_fname}')
            st.session_state['image'] = Image.open(new_img_path)
        
        # Remember the selected image option
        st.session_state['last_image_option'] = st.session_state.image_option

def image_to_server():
    """
    Copy the image (either original or cropped) to a static directory 
    and print the relative path for the image.
    """
    # Determine the destination path based on the image option
    if st.session_state.image_option == 'Original':
        static_image_path = os.path.join('static_og', os.path.basename(st.session_state['image_path']))
        shutil.copy(st.session_state["image_path"], os.path.join(st.session_state.static_folder_path_o, os.path.basename(st.session_state['image_path'])))
    elif st.session_state.image_option == 'Cropped':
        static_image_path = os.path.join('static_cr', os.path.basename(st.session_state['image_path']))
        shutil.copy(st.session_state["image_path"], os.path.join(st.session_state.static_folder_path_c, os.path.basename(st.session_state['image_path'])))

    # Print the relative path to the static directory
    relative_path_to_static = os.path.relpath(static_image_path, st.session_state.current_dir).replace('\\', '/')
    print(f"Adding to Zoom image server: {relative_path_to_static}")
    return relative_path_to_static

def display_image_options_buttons(relative_path_to_static):
    """
    Display buttons for different image options.
    The number and type of buttons displayed depends on st.session_state.use_extra_image_options.
    """
    # Define the Zoom link
    link = f'http://localhost:8000/{relative_path_to_static}'
    
    if st.session_state.use_extra_image_options:
        _, zoom_1, zoom_2, zoom_3, zoom_4, __ = st.columns([1,2,2,2,2,1])
        with zoom_1:
            if st.button('Show Original Image', use_container_width=True):
                st.session_state.image_option = 'Original'
                st.experimental_rerun()
        with zoom_2:
            if st.button('Zoom', use_container_width=True):
                webbrowser.open_new_tab(link)
        with zoom_3:
            if st.button('Toggle Fitted', use_container_width=True):
                st.session_state.is_fitted_image = not st.session_state.is_fitted_image
                st.session_state.set_image_size = 'Fitted' if st.session_state.is_fitted_image else st.session_state.set_image_size_previous
        with zoom_4:
            if st.button('Show Cropped Image', use_container_width=True):
                st.session_state.image_option = 'Cropped'
                st.experimental_rerun()
    else:
        _, zoom_1, zoom_2, zoom_3, __ = st.columns([1,2,2,2,1])
        with zoom_1:
            if st.button('Show Original Image', use_container_width=True):
                st.session_state.image_option = 'Original'
                st.experimental_rerun()
        with zoom_2:
            if st.button('Zoom', use_container_width=True):
                webbrowser.open_new_tab(link)
        with zoom_3:
            if st.button('Show Cropped Image', use_container_width=True):
                st.session_state.image_option = 'Cropped'
                st.experimental_rerun()

def display_scrollable_image():
    """
    Display the image from st.session_state in a scrollable container.
    The width and height of the container are determined by st.session_state values.
    """
    # Initialize the container
    con_image = st.empty()
    with con_image.container():
        # Determine the desired width based on st.session_state.set_image_size
        if st.session_state.set_image_size == "Auto Width":
            st.image(st.session_state['image'], caption=st.session_state['image_path'], use_column_width=True)
            return

        if st.session_state.set_image_size == "Custom":
            image_width = st.session_state.set_image_size_px
        elif st.session_state.set_image_size == "Large":
            image_width = 1500
        elif st.session_state.set_image_size == "Medium":
            image_width = 1100
        elif st.session_state.set_image_size == "Small":
            image_width = 800
        elif st.session_state.set_image_size == "Fitted":
            image_width = 600
        else:
            image_width = 1100  # For use_column_width=True

        # Convert the image to base64
        base64_image = image_to_base64(st.session_state['image'])

        # Embed the image with the determined width in the custom div
        img_html = f"""
        <div class='scrollable-image-container'>
            <img src='data:image/jpeg;base64,{base64_image}' alt='Image' style='width:{image_width}px'>
        </div>
        """

        # The CSS to make this container scrollable, with dynamic height based on st.session_state.set_image_size_pxh
        css = f"""
        <style>
            .scrollable-image-container {{
                overflow: auto;
                height: {st.session_state.set_image_size_pxh}vh;
                width: 70vw;
            }}
        </style>
        """

        # Apply the CSS and then the image
        st.markdown(css, unsafe_allow_html=True)
        st.markdown(img_html, unsafe_allow_html=True)

###############################################################
####################                    #######################
####################    Welcome Page    #######################
####################                    #######################
###############################################################
if 'data' not in st.session_state:
    st.session_state.data = None

if st.session_state.data is None:
    clear_directory()
    start_server()

    show_header_welcome()

    get_directory_paths(args)
    mapbox_key = prompt_for_mapbox_key()
    load_data(mapbox_key)

    if st.session_state.data is not None:
        st.experimental_rerun()

###############################################################
####################                    #######################
####################      Main App      #######################
####################                    #######################
###############################################################
if st.session_state.data is not None:
    show_header_main()

    # Initialize previous_row_to_edit if it's not already in session_state
    st.session_state.setdefault('previous_row_to_edit', None)

    # Set the overall layout. Right is for image things, left is for text things
    c_left, c_right = layout_image_proportion()

    # Organize the text groupings
    group_options = list(grouping.keys()) + ["ALL"]
    group_option = st.session_state.get("group_option", group_options[0])
    group_option_cols = c_left.columns(len(group_options))
    
    # Create a button for each category group, used for tracking
    for i, option in enumerate(group_options):
        if option in st.session_state.data.loc[st.session_state.row_to_edit, "track_edit"].split(","):
            if group_option_cols[i].button(option, use_container_width=True):
                st.session_state["group_option"] = option
                group_option = option
            
        else:
            group_option_cols[i].button(option, use_container_width=True, disabled=True)
        
    # Display a progress bar showing how many of the group_options are present in track_edit
    with c_left:
        update_progress_bar()

    # Layout for Form View (alternative is Spreadsheet View)
    if st.session_state.view_option == "Form View":

        with c_left:
            if (st.session_state.progress == 0) and group_options[0] not in st.session_state.data.loc[st.session_state.row_to_edit, "track_edit"]: 
                # Add default option if "track_edit" is empty and doesn't contain the default option already
                add_default_option_if_not_present()
                st.experimental_rerun()
            
            # Create the Previous and Next buttons, define 4 sub columns
            c_index, c_skip ,c_prev, c_next = st.columns([4,4,4,4])
            with c_prev:
                on_press_previous()
            with c_next:
                # Count the number of group options that have been selected
                # Only enable the 'Next' button if all group options have been selected
                on_press_next(group_options)
                        
            # Get the current row from the spreadsheet, show the index
            n_rows = len(st.session_state.data)
            with c_index:
                st.write(f"**Editing row {st.session_state.row_to_edit} / {n_rows-1}**")
            
            # Create the skip to bookmark button
            with c_skip:
                on_press_skip_to_bookmark()

            c_json, c_form = st.columns([4,4])
            # c_form, c_json = st.columns([4,4])
            
            # *** Display the spreadsheet rows in the form ***
            with c_form:
                con_form = st.empty()
                with con_form.container():
                    form_layout(group_option, grouping, color_map)

                on_press_confirm_content()

            ### Validate Fields TODO: add many more validation steps
            with c_json:
                validate_verbatim_coordinates()

        # Update the track_view column for the current row
        if st.session_state.access_option != 'Admin': # ONLY add views if in the label tab
            st.session_state.data.loc[st.session_state.row_to_edit, "track_view"] = 'True'
        

    ### Show the spreadsheet layout
    elif st.session_state.view_option == "Data Editor":
        with c_left:
            st.write("Skipping ahead (editing in the 'Form View' out of order) will cause issues if all 5 groups are selected while skipping ahead.")
            st.write("If skipping ahead, only use the 'ALL' option until returning to sequential editing.")
            # Reorder the columns to have "track_view" and "track_edit" at the beginning
            reordered_columns = ['track_view', 'track_edit'] + [col for col in st.session_state.data.columns if col not in ['track_view', 'track_edit']]
            st.session_state.data = st.session_state.data[reordered_columns]

            # If the view option is "Data Editor", create a new full-width container for the editor
            with st.container():
                edited_data = st.data_editor(st.session_state.data)
                b_color = "black"
                b_text = "Save Edits"
                b_label = f":{b_color}[{b_text}]"
                if st.button(label=b_label, type="primary", use_container_width=True):
                    # Save the edited data back to the session state data
                    st.session_state.data = edited_data
                    save_data()

                # Slider or number input to select the row
                # Only display the slider if there are 2 or more rows
                if len(st.session_state.data) >= 2:
                    slider_value = st.slider("Select a row to display its image", min_value=st.session_state.data.index[0], max_value=st.session_state.data.index[-1], value=int(st.session_state.row_to_edit))

                    # Only update the row_to_edit if slider value changes
                    if slider_value != st.session_state.row_to_edit:
                        st.session_state.row_to_edit = slider_value
                    save_data()
                    
                # Display the current row
                n_rows = len(st.session_state.data)-1
                st.write(f"**Showing image for row {st.session_state.row_to_edit} / {n_rows}**")
            c_json, c_form = st.columns([4,4])




    # check if the row_to_edit has changed
    if 'last_row_to_edit' not in st.session_state:
        st.session_state['last_row_to_edit'] = None

    # check if the row_to_edit has changed
    if st.session_state.row_to_edit != st.session_state.previous_row_to_edit:
        st.session_state.current_options = []
        st.session_state.previous_row_to_edit = st.session_state.row_to_edit


    # Only load JSON if row has changed
    with c_json:
        load_json_helper_files()

        display_json_helper_text()

        
    ### Display the image
    with c_right:
        image_path_and_load()

        if 'image' in st.session_state and 'last_image_option' in st.session_state:    

            # Add the image to the local server for the zoom functionality
            relative_path_to_static = image_to_server()

            # Two options for the image viewing buttons
            display_image_options_buttons(relative_path_to_static)

            # Display the configurable image viewer
            display_scrollable_image()



    st.header('Project Progress')

    # col_low_1, col_low_2, col_low_3, col_low_4, col_low_5, col_low_6, col_low_7, col_low_8,  = st.columns([1,1,1,1,1,1,1,1])
    last_true_index, last_fully_viewed = update_progress_bar_overall()
    # st.session_state['last_fully_viewed'] = last_fully_viewed
    # # update the 'last_row_to_edit' in the session state to the current 'row_to_edit'
    # st.session_state['last_row_to_edit'] = st.session_state.row_to_edit

    # with col_low_1:
    #     if st.button('Skip to last **fully** viewed',key=f"Skip_to_last_fully_viewed1"):
    #         st.session_state.row_to_edit = int(last_fully_viewed)
    #         st.experimental_rerun()

    # with col_low_2:
    #     if st.button('Skip to last viewed',key=f"Skip_to_last_viewed1"):
    #         st.session_state.row_to_edit = int(last_true_index)
    #         st.experimental_rerun()

    # with col_low_3:
    #     if st.button('Save Data'):
    #         save_data()

    
        
