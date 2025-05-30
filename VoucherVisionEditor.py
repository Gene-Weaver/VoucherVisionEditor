import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import json, os, sys, argparse, shutil, re, toml, math, yaml, tempfile, zipfile, base64, webbrowser, threading, subprocess, platform

from PIL import Image
from utils import *
from io import BytesIO
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_community.utilities import DuckDuckGoSearchAPIWrapper
from annotated_text import annotated_text
from datetime import datetime
from contextlib import contextmanager

import cProfile
import pstats

from utils import get_wfo_url, ScreenResolution
from text import HelpText

# For Table View
from streamlit.components.v1 import html
from itables import JavascriptFunction
import itables.options as opt
from itables import to_html_datatable, init_notebook_mode, show, JavascriptCode
from itables.downsample import as_nbytes, nbytes
from itables.sample_dfs import get_indicators
# init_notebook_mode(all_interactive=True)
opt.maxBytes = 0  # Set maxBytes to 0 to remove any size restrictions
opt.maxRows = 0   # No limit on number of rows
opt.maxColumns = 0  # No limit on number of columns


# pip install streamlit pandas Pillow openpyxl streamlit-aggrid
# Windows
# streamlit run your_script.py -- --SAVE_DIR /path/to/save/dir
# Linux
# export SAVE_DIR=/path/to/save/dir && streamlit run your_script.py

### To run:
# streamlit run VoucherVisionEditor.py -- 
# --base-path D:/D_Desktop/LM2/Asa_Gray/Transcription
# --save-dir D:/D_Desktop/LM2

# streamlit run VoucherVisionEditor.py -- 
# --base-path D:/Dropbox/LM2_Env/VoucherVision_Datasets/POC_chatGPT__2022_09_07_thru12_S3_jacortez_AllAsia/2022_09_07_thru12_S3_jacortez_AllAsia_2023_06_16__02-12-26
# --save-dir D:/D_Desktop/OUT

WORKING_DIR = os.path.dirname(os.path.realpath(__file__))
os.chdir(WORKING_DIR)
print(f"Current working dir: {os.getcwd()}")
st.set_page_config(layout="wide", 
                   page_icon='img/icon.ico', 
                   page_title='VoucherVision Editor',
                   menu_items={"Report a Bug": "https://forms.gle/kP8imC9JQTPLrXgg8","About":"VoucherVision was created and is maintained by William Weaver, University of Michigan. Please see doi:10.1002/ajb2.16256 for more information."},
                   initial_sidebar_state="expanded",)

LAST_UPDATED = "April 24, 2025 --- v3"
###########################################################################################################################
######## If true, this will let you host the project remotely
######## Otherwise all project info will be hosted inside VoucherVisionEditor/ on the local machine
###########################################################################################################################
if "USE_REMOTE" not in st.session_state:
    st.session_state.USE_REMOTE = False
    
if "project_dir" not in st.session_state:
    st.session_state.project_dir = ''
###########################################################################################################################
if "screen_width" not in st.session_state:
    screen = ScreenResolution()
    st.session_state.screen_width, st.session_state.screen_height = screen.get_smallest_monitor()

if "start_editing" not in st.session_state:
    st.session_state.start_editing = False

if "hide_columns_in_editor" not in st.session_state:
    st.session_state.hide_columns_in_editor = []

# Initialize Streamlit Session State if it hasn't been initialized yet
if "row_to_edit" not in st.session_state:
    st.session_state.row_to_edit = 0

if 'data' not in st.session_state:
    st.session_state.data = None

if "file_name" not in st.session_state:
    st.session_state.file_name = None

if "user_input" not in st.session_state:
    st.session_state.user_input = {}

if "table_height_holder" not in st.session_state:
    st.session_state.table_height_holder = 0

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

if "entries_per_page" not in st.session_state:
    st.session_state.entries_per_page = 10

if "progress_index" not in st.session_state:
    st.session_state.progress_index = 0

if "access_option" not in st.session_state:
    st.session_state.access_option = 'Labeler'

if "prompt_mapping" not in st.session_state:
    st.session_state.prompt_mapping = None
# Store the previous value of st.session_state.access_option
if 'previous_access_option' not in st.session_state:
    st.session_state.previous_access_option = 'Labeler'

if 'image_option' not in st.session_state:
    # st.session_state.image_option = 'Cropped'
    st.session_state.image_option = 'Original'

if 'last_image_option' not in st.session_state:
    st.session_state.last_image_option = ''

if 'default_to_original' not in st.session_state:
    st.session_state.default_to_original = True

if 'view_option' not in st.session_state:
    st.session_state.view_option = "Form View"

if 'show_helper_text' not in st.session_state:
    st.session_state.show_helper_text = False

if 'set_image_size' not in st.session_state:
    st.session_state.set_image_size = 'Custom'

if 'set_image_size_previous' not in st.session_state:
    st.session_state.set_image_size_previous = 'Custom'

if 'set_image_size_px' not in st.session_state:
    if st.session_state.screen_height >= 1600:
        st.session_state.set_image_size_px = 1000
    elif st.session_state.screen_height >= 1400:
        st.session_state.set_image_size_px = 900
    elif st.session_state.screen_height >= 1100:
        st.session_state.set_image_size_px = 850
    elif st.session_state.screen_height >= 1000:
        st.session_state.set_image_size_px = 800
    elif st.session_state.screen_height >= 850:
        st.session_state.set_image_size_px = 650
    else:
        st.session_state.set_image_size_px = 500

if 'set_image_size_pxh' not in st.session_state:
    st.session_state.set_image_size_pxh = 80

if 'set_map_height_pxh' not in st.session_state:
    st.session_state.set_map_height_pxh = 200

if 'image_fill' not in st.session_state:
    st.session_state.image_fill = "More - Image Right"

if 'use_extra_image_options' not in st.session_state:
    st.session_state.use_extra_image_options = False

if 'is_fitted_image' not in st.session_state:
    st.session_state.is_fitted_image = False

if 'fitted_image_width' not in st.session_state:
    st.session_state.fitted_image_width = 600

if 'n_columns' not in st.session_state:
    st.session_state.n_columns = 26

if 'working_file' not in st.session_state:
    st.session_state.working_file = None  

if 'prompt_name' not in st.session_state:
    st.session_state.prompt_name = None  

if 'prompt_json' not in st.session_state:
    st.session_state.prompt_json = None  

if 'form_hint_location' not in st.session_state:
    st.session_state.form_hint_location = 'Left'     

if 'search_term' not in st.session_state:
    st.session_state.search_term = ''

if 'http_server_port' not in st.session_state:
    st.session_state.http_server_port = 8000

if 'color_map_order' not in st.session_state:
    st.session_state.color_map_order = ["#7fbfff", "#f6a14f", "#48ca48", "#bf7fbf", "#ff3333" , "#787878", "#ff00fb"]

if 'color_map_order_text' not in st.session_state:
    st.session_state.color_map_order_text = [":blue", ":orange", ":green", ":violet", ":red" , ":gray", ":rainbow"]

if 'color_map_json' not in st.session_state:
    st.session_state.color_map_json = {}

if 'color_map_text' not in st.session_state:
    st.session_state.color_map_text = {}

if 'wfo_match_level' not in st.session_state:
    st.session_state.wfo_match_level = "No Match"

if 'image_rotation' not in st.session_state:
    st.session_state.image_rotation = "0"

if 'image_rotation_change' not in st.session_state:
    st.session_state.image_rotation_change = True

if 'relative_path_to_static' not in st.session_state:
    st.session_state.relative_path_to_static = ''

if 'image_path' not in st.session_state:
    st.session_state.image_path = ''

if 'current_time' not in st.session_state:
    st.session_state.current_time = 'NA'

if 'hide_fields' not in st.session_state:
    st.session_state.hide_fields = []

if 'add_fields' not in st.session_state:
    st.session_state.add_fields = {}

if 'set_map_height' not in st.session_state:
    st.session_state.set_map_height = True
    
if 'user_uniqname' not in st.session_state:
    st.session_state.user_uniqname = ''

if 'user_uniqname_key' not in st.session_state:
    st.session_state.user_uniqname_key = 6787987987
    
if 'dialog_closed' not in st.session_state:
    st.session_state.dialog_closed = False

if 'group_options_tracker' not in st.session_state:
    st.session_state.group_options_tracker = {}

if 'n_manual_data' not in st.session_state:
    st.session_state.n_manual_data = 0   

if 'n_total_data' not in st.session_state:
    st.session_state.n_total_data = 0   
    
    
if 'tool_access' not in st.session_state:
    st.session_state.tool_access = {
        'show_skip_specimen': False,
        'form': True, #ALWAYS TRUE
        'arrow': True,
        'hints': True,
        'ocr': False,
        'wfo_badge': True,
        'taxa_links': True,
        'wfo_links': True,
        'additional_info': True,
        'cap': True,
        'search': False,
    }  
if 'pwd' not in st.session_state:
    st.session_state.pwd = 'vouchervisionadmin'

if 'image_rotation_previous' not in st.session_state:
    st.session_state.image_rotation_previous = ''

if 'location_google_search' not in st.session_state:
    st.session_state.location_google_search = "Top" # "Top", "Hint Panel", "Bottom"

if 'google_search_new_window' not in st.session_state:
    st.session_state.google_search_new_window = False #TODO


if 'grouping' not in st.session_state:
    st.session_state.grouping = None

# Initialize a state to know whether the button was clicked or not
if "button_clicked" not in st.session_state:
    st.session_state.button_clicked = False

if "form_width" not in st.session_state:
    st.session_state.wrap_len = 30
    st.session_state.form_width_1 = 30
    st.session_state.form_width_2 = 50

if "distance_GPS_warn" not in st.session_state: # Can be configured
    st.session_state.distance_GPS_warn = 100

if 'zoom_dist' not in st.session_state: # Can be configured
    st.session_state.zoom_dist = 3000

if 'pinpoint' not in st.session_state:
    st.session_state.pinpoint = "Broad"

if 'coordinates_dist' not in st.session_state:
    st.session_state.coordinates_dist = None

if 'fullpath_working_file' not in st.session_state:
    st.session_state.fullpath_working_file = None

if 'dir_home' not in st.session_state:
    st.session_state.dir_home = os.path.dirname(__file__)
    st.session_state.dir_settings = os.path.join(st.session_state.dir_home,'settings')
    st.session_state.settings_file = ""

if 'data' not in st.session_state:
    st.session_state.data = None

if 'wiki_file_list' not in st.session_state:
    st.session_state.wiki_file_list = []

if 'wiki_file_dict' not in st.session_state:
    st.session_state.wiki_file_dict = {}

if 'search_results_duckduckgo' not in st.session_state:
    st.session_state.search_results_duckduckgo = None

if 'search_info_plants' not in st.session_state:
    st.session_state.search_info_plants = ['order','family','scientificName', 'scientificNameAuthorship', 'genus','subgenus', 'specificEpithet', 'infraspecificEpithet',]
if 'search_info_geo' not in st.session_state:
    st.session_state.search_info_geo = ['country','stateProvince','county', 'municipality', 'minimumElevationInMeters','maximumElevationInMeters', 'locality', 'habitat','decimalLatitude', 'decimalLongitude', 'verbatimCoordinates',]
if 'search_info_people' not in st.session_state:
    st.session_state.search_info_people = ['identifiedBy','recordedBy',]

if 'BASE_PATH' not in st.session_state:
    st.session_state.BASE_PATH = ''

if 'BASE_PATH_MANUAL' not in st.session_state:
    st.session_state.BASE_PATH_MANUAL = None

if 'bp_text' not in st.session_state:
    st.session_state.bp_text = '''
    ## Running VVE from the command line (optional)
    #### Save Directory and Base Path Configuration 
    When launching the VoucherVision Editor (VVE) from the command line, two optional arguments can be specified: `--save-dir` and `--base-path`. 

    - `--save-dir` defines where the edited file will be saved. VVE never overwrites the original transcription file. This must be the full file path to where the edited transcription.xlsx should be saved. If you need to pause an editing run and resume it at a later time, then the last "edited" file becomes the new input file, but `--save-dir` can remain the same because it will simply increment after each save.

    - `--base-path` optional. Reroutes the file paths in the original transcription file ***if the files have been moved***. The original transcription file saves the full paths to the transcription JSON files, cropped labels images, and the original full specimen images. If the computer where VVE is running has access to these files and those file locations have not changed, then the `--base-path` option is not needed. But in the event that the original file paths are broken, this will rebuild the file paths to the new locations.

    If `--save-dir` and `--base-path` are not provided in the command line arguments, you can specify them below.
    '''

if 'save_dir_help' not in st.session_state:
    st.session_state.save_dir_help = """
    Defines where the edited file will be saved. 
    VVE never overwrites the original transcription file. 
    This must be the full file path to where the edited transcription.xlsx should be saved. 
    If you need to pause an editing run and resume it at a later time, 
    then the last "edited" file becomes the new input file, 
    but --save-dir can remain the same because it will simply increment after each session.
    """
    
if 'base_path_help' not in st.session_state:
    st.session_state.base_path_help = """
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

parser = argparse.ArgumentParser(description='Define save location of edited file.')

# Add parser argument for save directory
parser.add_argument('--save-dir', type=str, default=None,
                    help='Directory to save output files')
parser.add_argument('--base-path', type=str, default='',
                    help='New base path to replace the existing one, up to "/Transcription"')
parser.add_argument('--prompt-version', type=str, default='',
                    help='Prompt version used for VoucherVision. V1 has 26 total columns. V2 has 30 column (all headers are lowercase, have underscores)')

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
def setup_streamlit_config(mapbox_key=None):
    # Define the directory path and filename
    dir_path = ".streamlit"
    file_path = os.path.join(dir_path, "config.toml")

    # Check if directory exists, if not create it
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)

    # If the mapbox_key is empty, and the config file already has a mapbox key, don't overwrite the file
    # if mapbox_key == None:
    #     if os.path.exists(file_path):
    #         config_data = toml.load(file_path)
    #         existing_key = config_data.get('mapbox', {}).get('token', None)
    #         if existing_key is not None and existing_key != '':
    #             return
    
    # Create or modify the file with the provided content
    config_content = f"""
    [theme]
    primaryColor = "#00ff00"
    backgroundColor="#1a1a1a"
    secondaryBackgroundColor="#303030"
    textColor = "cccccc"

    [server]
    enableStaticServing = true
    runOnSave = true
    port = 8523

    [runner]
    fastReruns = false
    """

    if mapbox_key:
        config_content += f"""
        [mapbox]
        token = "{mapbox_key}"
        """

    with open(file_path, "w") as f:
        f.write(config_content.strip())

###############################################################
#################       Definitions        ####################
###############################################################
# st.session_state.color_map = {
#     "TAXONOMY": 'blue', 
#     "GEOGRAPHY": 'orange', 
#     "LOCALITY": 'green',
#     "COLLECTING": 'violet', 
#     "MISC": 'red', 
#     # "OCR": '#7fbfff', 
# }

# st.session_state.color_map_json = {
#     "TAXONOMY": "#7fbfff", # pastel blue
#     "GEOGRAPHY": "#f6a14f",  # pastel orange
#     "LOCALITY": "#48ca48", # pastel green
#     "COLLECTING": "#bf7fbf",  # pastel purple
#     "MISC": "#ff3333",  # pastel red
# }

# def set_column_groups():
#     # if st.session_state.n_columns == 26: # Version 1 prompts
#     if st.session_state.prompt_version == 'v1':
#         st.session_state.grouping = {
#             "TAXONOMY": ["Catalog Number", "Genus", "Species", "subspecies", "variety", "forma",],
#             "GEOGRAPHY": ["Country", "State", "County", "Verbatim Coordinates",],
#             "LOCALITY": ["Locality Name", "Min Elevation", "Max Elevation", "Elevation Units",],
#             "COLLECTING": ["Datum","Cultivated","Habitat","Collectors","Collector Number", "Verbatim Date","Date", "End Date",],
#         }
#     # elif st.session_state.n_columns == 30: # Version 2 prompts
#     if st.session_state.prompt_version == 'v2':
#         st.session_state.grouping = {
#             "TAXONOMY": ["catalog_number", "genus", "species", "subspecies", "variety", "forma",],
#             "GEOGRAPHY": ["country", "state", "county", "verbatim_coordinates","decimal_coordinates"],
#             "LOCALITY": ["locality_name", "min_elevation", "max_elevation", "elevation_units",],
#             "COLLECTING": ["datum","cultivated","habitat","plant_description","collectors","collector_number", "determined_by", "verbatim_date","date", "end_date",],
#         }
#     else:
#         raise
def set_column_groups():
    try:
        with open(st.session_state.settings_file, 'r') as file:
            st.session_state.settings_file_dict = yaml.safe_load(file)
        st.session_state.add_fields = st.session_state.settings_file_dict['editor']['add_fields']
        st.session_state.hide_fields = st.session_state.settings_file_dict['editor']['hide_fields']
    except:
        pass


    mapping = st.session_state.prompt_mapping
    # Initialize an empty dictionary for the new grouping
    new_grouping = {}

    ind = 0
    temp_map = {}
    # Iterate over the mapping
    for group, columns in mapping.items():
        temp_map[group] = ind
        # Create a new group in the new_grouping dictionary with the list of columns
        if columns:
            new_grouping[group] = columns
            st.session_state.color_map_json[group] = st.session_state.color_map_order[ind]
            st.session_state.color_map_text[group] = st.session_state.color_map_order_text[ind]
            ind += 1
            

    # Add the new columsn to the list
    for group, columns in st.session_state.add_fields.items():
        if (group in new_grouping) and columns:
            # Group exists, append the columns if not empty
            if not isinstance(new_grouping[group], list):
                new_grouping[group] = [new_grouping[group]]  # Ensure it's a list
            new_grouping[group].extend(columns)  # Append new columns
            
        else:
            st.session_state.color_map_json[group] = st.session_state.color_map_order[ind]
            st.session_state.color_map_text[group] = st.session_state.color_map_order_text[ind]
            # Group doesn't exist or has no columns, assign new columns
            new_grouping[group] = (columns)
            ind += 1

     
    # Add the new columns to the CSV

            
    # Update the st.session_state.grouping with the new grouping
    st.session_state.grouping = new_grouping


###############################################################
#################          Utils           ####################
###############################################################
def unzip_and_setup_path(uploaded_file, target_dir):
    if uploaded_file is not None:
        with st.spinner(f'Extracting files to [{target_dir}]'):
            with zipfile.ZipFile(uploaded_file, 'r') as zip_ref:
                zip_ref.extractall(target_dir)
        st.success("File unpacked successfully")


# def upload_and_unzip():
#     project_dir = os.path.join(st.session_state.dir_home, 'projects')
#     os.makedirs(project_dir, exist_ok=True)

#     uploaded_file = st.file_uploader("Add a .zip file to the projects folder. Once added, you can select the project and then choose a transcription file to edit. ", 
#                                      type='zip',accept_multiple_files=False,)
#     if uploaded_file is not None:
#         # Construct the target directory path
#         # Assuming `dir_home` and `projects` are defined or replace with actual values
#         filename_zip = uploaded_file.name
#         base_filename = filename_zip.rsplit('.', 1)[0]  # Remove the .zip extension
#         target_dir = os.path.join(project_dir, base_filename)
#         os.makedirs(target_dir, exist_ok=True)  # Create target directory if it doesn't exist
        
#         # Unzip and set up the path
#         unzip_and_setup_path(uploaded_file, target_dir)

#         # Update BASE_PATH to the new directory containing the unpacked files
#         st.session_state.BASE_PATH = target_dir
#         print(f"BASE = {target_dir}")

#     subdirs = [d for d in os.listdir(project_dir) if os.path.isdir(os.path.join(project_dir, d))]

#     # Create a select box for choosing a subdirectory
#     selected_subdir = st.selectbox("Select a project:", subdirs)
#     st.session_state.BASE_PATH = os.path.join(project_dir, selected_subdir)
#     st.info(f"Working from: {st.session_state.BASE_PATH}")
def resolve_actual_path(directory):
    """Resolve the actual path to handle different mappings."""
    return os.path.realpath(directory)

def get_mounted_volumes():
    """Returns a list of currently mounted volumes on macOS."""
    volumes = []
    
    if platform.system() == 'Darwin':  # macOS
        volumes_dir = '/Volumes/'
        if os.path.exists(volumes_dir):
            volumes = [os.path.join(volumes_dir, d) for d in os.listdir(volumes_dir) if os.path.isdir(os.path.join(volumes_dir, d))]
    
    return volumes
    
def find_available_project_dir(project_dir_list):
    """Find the available project directory from a list of paths."""
    if not project_dir_list:
            raise ValueError("The project directory list is empty.")
    
    system_platform = platform.system()

    # Handle Windows paths
    if system_platform == 'Windows':
        for directory in project_dir_list:
            resolved_path = resolve_actual_path(directory)
            
            # If the resolved path exists, return it
            if os.path.exists(resolved_path):
                return resolved_path
            

    # Handle macOS paths
    elif system_platform == 'Darwin':
        mounted_volumes = get_mounted_volumes()

        # Try replacing "S:" with each mounted volume and check if path exists
        for directory in project_dir_list:
            for volume in mounted_volumes:
                print(f"Mounted Volume: {volume}, DIR: {directory}")
                possible_mappings = [
                    directory.replace("S:", volume),
                    directory.replace("Curatorial Projects/VoucherVision", "VoucherVision").replace("S:", volume)
                ]
                print(f"     Possible Mappings: {possible_mappings}")
                for path in possible_mappings:
                    if os.path.exists(path):
                        return os.path.realpath(path)  # Return the resolved path directly

    # If none of the paths resolve, raise an error
    return None



@st.dialog("Add new user")
def add_new_user():
    st.warning(f"Do you want to add {st.session_state.user_uniqname} as a new user?")
    c1, c2 = st.columns(2)
    with c1:
        if st.button(f"No"):
            st.session_state.user_uniqname = ''
            st.session_state.project_dir = ''
            st.session_state.user_uniqname_key +=1
            st.rerun()
    with c2:
        if st.button(f"Add :violet-background[{st.session_state.user_uniqname}]"):
            if st.session_state.USE_REMOTE:
                st.session_state.project_dir = os.path.join(st.session_state.BASE_PATH_MANUAL, st.session_state.user_uniqname)
            else:
                st.session_state.project_dir = os.path.join(st.session_state.dir_home, 'projects', st.session_state.user_uniqname)

            os.makedirs(st.session_state.project_dir, exist_ok=True)
            st.rerun()
    

def upload_and_unzip():
    file_path = os.path.join(st.session_state.dir_home, 'settings', 'default.yaml')

    c_left, c_right = st.columns([8,2])

    with c_right:
        st.markdown(""":violet-background[NOTE:]\n\n- Refreshing your browser will restart VoucherVisionEditor from this page and reset all settings\n\n- In the Editor, every change you make is immediately saved to the session's .xlsx file""")
        st.markdown(f"Last Updated: {LAST_UPDATED}")
    with c_left:

        # Load existing settings
        st.session_state.settings = load_yaml_settings(file_path)
        if st.session_state.settings is None:
            st.session_state.settings = {
                'editor': {
                    'hide_fields': [],
                    'add_fields': {},
                }
                ,'locations': {
                    'project_dir': 'local',
                }
            }
            # save_yaml_settings(file_path, st.session_state.settings)

        project_dir_list = st.session_state.settings['locations']['project_dir']

        if st.session_state.settings['locations']['project_dir'] != "local":
            try:
                st.session_state.USE_REMOTE = True

                # Check for the first available directory in the list
                available_project_dir = None

                available_project_dir = find_available_project_dir(project_dir_list)

                if available_project_dir is None:
                    # If no directories are found, raise an error and disable remote usage
                    raise FileNotFoundError("None of the project directories are accessible")
                else:
                    project_dir_list = [available_project_dir]

                # if platform.system() == 'Darwin':
                    # raise NotImplementedError("macOS (Darwin) handling is not implemented yet")

            except Exception as e:
                st.session_state.USE_REMOTE = False
                # if platform.system() == 'Darwin':
                    # raise NotImplementedError("macOS (Darwin) handling is not implemented yet")

                st.error(f"The settings/default.yaml file location for the project_dir is set to {project_dir_list} but none are accessible. VoucherVisionEditor will default to loading/storing data locally within VoucherVisionEditor/projects/")
                st.error(str(e))
        else:
            st.session_state.USE_REMOTE = False

        # Remote file handling
        if st.session_state.USE_REMOTE:
            if isinstance(project_dir_list, str):
                project_dir_list = [project_dir_list]
            st.session_state.BASE_PATH_MANUAL = st.selectbox("Set Project Directory", options=project_dir_list, index=project_dir_list.index(available_project_dir), disabled=True)
            
            if st.session_state.BASE_PATH_MANUAL is not None:
                st.session_state.user_uniqname = st.text_input("Set Uniqname", value=st.session_state.user_uniqname, key=st.session_state.user_uniqname_key)
                if st.session_state.user_uniqname == '':
                    st.warning("Uniqname cannot be empty. Please enter your Uniqname.")
                else:
                    if not os.path.exists(os.path.join(st.session_state.BASE_PATH_MANUAL, st.session_state.user_uniqname)):
                        add_new_user()
                    else:
                        st.session_state.project_dir = os.path.join(st.session_state.BASE_PATH_MANUAL, st.session_state.user_uniqname)
                        
        # Local file handling
        else:
            st.session_state.user_uniqname = st.text_input("Set Uniqname", value=st.session_state.user_uniqname, key=st.session_state.user_uniqname_key)
            if st.session_state.user_uniqname == '':
                st.warning("Uniqname cannot be empty. Please enter your Uniqname.")
            else:
                if not os.path.exists(os.path.join(st.session_state.dir_home, 'projects', st.session_state.user_uniqname)):
                    add_new_user()
                else:
                    st.session_state.project_dir = os.path.join(st.session_state.dir_home, 'projects', st.session_state.user_uniqname)

            
        if st.session_state.project_dir != '' and st.session_state.user_uniqname != '':

            uploaded_file = st.file_uploader("Add a .zip file to the projects folder. Once added, you can select the project and then choose a transcription file to edit.", 
                                            type='zip', accept_multiple_files=False)
            # Initialize an indicator for a newly uploaded project
            new_project_added = False

            if uploaded_file is not None:
                # Construct the target directory path
                filename_zip = uploaded_file.name
                base_filename = filename_zip.rsplit('.', 1)[0]  # Remove the .zip extension
                target_dir = os.path.join(st.session_state.project_dir, base_filename)
                
                if not os.path.exists(target_dir):
                    os.makedirs(target_dir, exist_ok=True)  # Create target directory if it doesn't exist
                    # Unzip and set up the path
                    unzip_and_setup_path(uploaded_file, target_dir)
                    uploaded_file = None

                # Indicate a new project has been added to update BASE_PATH later
                new_project_added = True
                print(f"BASE = {target_dir}")
            

            # Initialize an empty list to store subdirectories
            subdirs = []
            # Iterate through all items in the project directory
            for item in os.listdir(st.session_state.project_dir):
                # Create the full path of the item
                item_path = os.path.join(st.session_state.project_dir, item)
                
                # Check if the item is a directory and not named "CONFIG"
                if os.path.isdir(item_path) and item != "CONFIG":
                    # If it's a valid subdirectory, add it to the subdirs list
                    subdirs.append(item)
            
            # Create a select box for choosing a subdirectory
            selected_subdir = st.selectbox("Select a project:", subdirs)

            

            # # Update BASE_PATH based on the user's actions
            # if new_project_added:
            #     # If a new project was uploaded, use its path
            #     st.session_state.BASE_PATH = target_dir
            # elif selected_subdir:
            #     # Otherwise, update BASE_PATH to the selected subdirectory
            #     st.session_state.BASE_PATH = os.path.join(project_dir, selected_subdir)

            #     st.info(f"Working from: {st.session_state.BASE_PATH}")
            # else:
            #     pass


            # Update BASE_PATH based on the user's actions
            if new_project_added:
                # If a new project was uploaded, use its path
                st.session_state.BASE_PATH = os.path.join(st.session_state.project_dir, selected_subdir)
            elif selected_subdir:
                # Otherwise, update BASE_PATH to the selected subdirectory
                st.session_state.BASE_PATH = os.path.join(st.session_state.project_dir, selected_subdir)

                st.info(f"Working from: {st.session_state.BASE_PATH}")
            else:
                pass


    

    


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
# def save_data():
#     # Check the file extension and save to the appropriate format
#     if st.session_state.file_name.endswith('.csv'):
#         file_path = os.path.join(st.session_state.SAVE_DIR, st.session_state.file_name)
#         st.session_state.data.to_csv(file_path, index=False)
#         # st.success('Saved (CSV)')
#         print(f"Saved (CSV) {file_path}")
#     elif st.session_state.file_name.endswith('.xlsx'):
#         file_path = os.path.join(st.session_state.SAVE_DIR, st.session_state.file_name)
#         st.session_state.data.to_excel(file_path, index=False)
#         # st.success('Saved (XLSX)')
#         print(f"Saved (XLSX) {file_path}")
#     else:
#         st.error('Unknown file format.')
def save_data_skipped(new_skipped_data):
    try:
        # st.session_state.data = pd.read_excel(st.session_state.BASE_PATH_transcription_LLM, dtype=str)
        file_path = os.path.join(st.session_state.SAVE_DIR, st.session_state.file_name_skipped)
        # Check if skipped file already exists
        if os.path.exists(file_path):
            # Load existing skipped data
            existing_data = pd.read_excel(file_path, dtype=str)
            
            # Check for duplicate based on the first column value
            first_column = existing_data.columns[0]
            if new_skipped_data[first_column].iloc[0] not in existing_data[first_column].values:
                # Append if no duplicate
                updated_data = pd.concat([existing_data, new_skipped_data], ignore_index=True)
                updated_data.to_excel(file_path, index=False)
                print(f"Appended to existing file (XLSX) {file_path}")
            else:
                print(f"Duplicate row based on {first_column}, skipping save.")
        else:
            # Save initial headers and first row if file does not exist
            new_skipped_data.to_excel(file_path, index=False)
            print(f"Created new file and saved (XLSX) {file_path}")
            
    except Exception as e:
        print(f"Error occurred: {e}")
        st.error(f'Error saving the file: {e}')



def save_data():
    # Check the file extension and save to the appropriate format
    # if st.session_state.file_name.endswith('.csv'):
    #     file_path = os.path.join(st.session_state.SAVE_DIR, st.session_state.file_name)
    #     st.session_state.data.to_csv(file_path, index=False)
    #     # st.success('Saved (CSV)')
    #     print(f"Saved (CSV) {file_path}")
    # elif st.session_state.file_name.endswith('.xlsx'):
    try:
        # Ensure the file path is absolute
        # save_dir = st.session_state.SAVE_DIR
        # if not os.path.isabs(save_dir):
            # save_dir = os.path.abspath(save_dir)
        
        file_path = os.path.join(st.session_state.SAVE_DIR, st.session_state.file_name)
        st.session_state.data_edited.to_excel(file_path, index=False)
        print(f"Saved (XLSX) {file_path}")
    except Exception as e:
        print(f"Error occurred: {e}")
        st.error(f'Error saving the file: {e}')
        
def create_save_dir(transcription_index, add_prefix = False):
    
    # Use the first path from the 'path_to_content' column as a base to determine the directory
    first_path_to_content = st.session_state.data['path_to_content'][0]

    # Split the path into components, handling drive letters separately on Windows
    # Handle platform-specific path splitting
    if platform.system() == 'Windows':
        # On Windows, use os.path.splitdrive to handle drive letters
        drive, path_tail = os.path.splitdrive(first_path_to_content)
        parts = path_tail.split(os.path.sep)
    elif platform.system() == 'Darwin':
        # On macOS, there's no drive letter, treat the path as Unix-style
        drive = ''  # No drive on macOS, so keep it empty
        parts = first_path_to_content.split(os.path.sep)

        # If the first element is empty (leading '/'), remove it
        if parts[0] == '':
            parts = parts[1:]
    
    # Check if we have a valid transcription index
    if transcription_index is None or transcription_index >= len(parts):
        raise ValueError("Transcription index is not found in the path")

    # Construct the SAVE_DIR from the path
    if platform.system() == 'Darwin':
        save_dir = os.path.join('/', *parts[:transcription_index ])#+ 3])                                   ### TODO check to see if it works for brad still
    else:
        save_dir = os.path.join(drive + os.path.sep, *parts[:transcription_index + 1])
    # macOS-specific adjustment: prepend '/' to make sure the path is absolute
    # if platform.system() == 'Darwin':
    #     print(f"     Adding leading / for macOS")
    #     print(f"     --> {save_dir}")
    #     save_dir = os.path.join('/', save_dir)  # Ensure the path is absolute
    #     print(f"     --> {save_dir}")

    # Ensure the directory exists, create it if it doesn't
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    # Set SAVE_DIR in session state
    st.session_state.SAVE_DIR = save_dir

    # For debugging: print the final save directory
    print(f"Save directory --> {st.session_state.SAVE_DIR}")

def get_current_datetime():
    # Get the current date and time
    now = datetime.now()
    # Format it as a string, replacing colons with underscores
    datetime_iso = now.strftime('%Y_%m_%dT%H_%M_%S')
    return datetime_iso

def load_notes():
    # Check if the file exists
    if not os.path.exists(st.session_state.BASE_PATH_notes):
        # File does not exist, create it with the initial dict
        st.session_state.notes_data = {"NOTES": ""}
        
        # Ensure the directory exists before writing the file
        os.makedirs(os.path.dirname(st.session_state.BASE_PATH_notes), exist_ok=True)
        
        # Write the initial data to the file
        with open(st.session_state.BASE_PATH_notes, 'w') as file:
            json.dump(st.session_state.notes_data, file)
    else:
        # File exists, load its contents into session state
        with open(st.session_state.BASE_PATH_notes, 'r') as file:
            st.session_state.notes_data = json.load(file)

def save_notes(text):
    # Create the data structure to save
    notes_data = {"NOTES": text}
    
    # Ensure the directory exists before writing the file
    os.makedirs(os.path.dirname(st.session_state.BASE_PATH_notes), exist_ok=True)
    
    # Write the data to the file
    with open(st.session_state.BASE_PATH_notes, 'w') as file:
        json.dump(notes_data, file)

    # Optionally update session state with the saved text
    st.session_state.notes_data = notes_data

# C:\Users\Will\Downloads\mistralmed_pv5_trOCRhand_angio
def load_data():
    if 'data' not in st.session_state or st.session_state.data is None:
        if st.session_state.BASE_PATH:
            st.session_state.BASE_PATH_transcription = os.path.join(st.session_state.BASE_PATH, 'Transcription')
            st.session_state.BASE_PATH_transcription_LLM = os.path.join(st.session_state.BASE_PATH, 'Transcription', 'transcribed.xlsx')
            st.session_state.BASE_PATH_transcription_LLM_prior = os.path.join(st.session_state.BASE_PATH, 'Transcription', 'transcribed_prior_to_subsetting.xlsx')
            st.session_state.BASE_PATH_notes = os.path.join(st.session_state.BASE_PATH, 'Transcription', 'notes.json')
            load_notes()

            xlsx_LLM = [st.session_state.BASE_PATH_transcription_LLM]
            xlsx_files = [file for file in os.listdir(st.session_state.BASE_PATH_transcription) if file.endswith('.xlsx')]
            st.session_state.LLM_file = st.selectbox(
                "LLM Transcription",
                xlsx_LLM,
                index=0,
                placeholder="",
                disabled=True,
                help=HelpText.LLMTranscription,
            )
            xlsx_files = [file for file in os.listdir(st.session_state.BASE_PATH_transcription) if file.endswith('.xlsx')]
            st.session_state.working_file = st.selectbox(
                "Select the transcription file you would like to edit",
                xlsx_files,
                index=None,
                placeholder="",
            )

                

            if st.session_state.working_file:
                st.session_state.fullpath_working_file = os.path.join(st.session_state.BASE_PATH_transcription, st.session_state.working_file)


                if os.path.exists(st.session_state.fullpath_working_file):
                    
                    
                    st.session_state.prompt_name = [file for file in os.listdir(os.path.join(st.session_state.BASE_PATH_transcription, 'Prompt_Template')) if file.endswith('.yaml')][0]
                    st.session_state.fullpath_prompt = os.path.join(st.session_state.BASE_PATH_transcription, 'Prompt_Template', st.session_state.prompt_name)

                    st.session_state.wiki_file_list = [file for file in os.listdir(os.path.join(st.session_state.BASE_PATH_transcription, 'Individual_Wikipedia')) if file.endswith('.json')]
                    for wiki_file in st.session_state.wiki_file_list:
                        fname = os.path.basename(wiki_file).split(".")[0]
                        st.session_state.wiki_file_dict[fname] = os.path.join(st.session_state.BASE_PATH_transcription, 'Individual_Wikipedia', wiki_file)

                    # Read the YAML file and convert it to a JSON object
                    with open(st.session_state.fullpath_prompt, 'r') as file:
                        st.session_state.prompt_json = yaml.safe_load(file)
                        st.session_state.prompt_mapping = st.session_state.prompt_json['mapping']

                    st.session_state.data = pd.read_excel(st.session_state.BASE_PATH_transcription_LLM, dtype=str)
                    st.session_state.n_total_data = st.session_state.data.shape[0]

                    # Exclude rows where 'country' contains 'X' or 'x' (case-insensitive)
                    # BUT WE NEED TO HIDE IT, NOT REMOVE THE ROW
                    manual_data = st.session_state.data[~st.session_state.data['country'].str.strip().str.lower().eq('x')]
                    st.session_state.n_manual_data = manual_data.shape[0]

                    st.session_state.n_columns = st.session_state.data.shape[1]

                    set_column_groups()

                    # Rename the new file at the time of editing
                    st.session_state.current_time = get_current_datetime()
                    tracker = '__edited__'
                    if tracker in st.session_state.working_file:
                        print("OPT1")
                        base = st.session_state.working_file.split(tracker)[0]
                        st.session_state.file_name = f"{base}{tracker}{st.session_state.current_time}.xlsx"
                    else:  # new transcription
                        print("OPT2")
                        st.session_state.file_name = f"{st.session_state.working_file.split('.')[0]}{tracker}{st.session_state.current_time}.xlsx"

                    # Name for transcribed_skipped.xlsx
                    st.session_state.file_name_skipped = "transcribed_skipped.xlsx"
                    st.session_state.file_name_prior_to_subsetting = "transcribed_prior_to_subsetting.xlsx"
                    
                    # If BASE_PATH is provided, replace old base paths in the dataframe
                    if st.session_state.BASE_PATH != '':
                        st.session_state.data['path_to_crop'] = st.session_state.data['path_to_crop'].apply(lambda old_path: replace_base_path(old_path, st.session_state.BASE_PATH, 'crop'))
                        st.session_state.data['path_to_original'] = st.session_state.data['path_to_original'].apply(lambda old_path: replace_base_path(old_path, st.session_state.BASE_PATH, 'original'))
                        st.session_state.data['path_to_helper'] = st.session_state.data['path_to_helper'].apply(lambda old_path: replace_base_path(old_path, st.session_state.BASE_PATH, 'jpg'))
                        st.session_state.data['path_to_content'] = st.session_state.data['path_to_content'].apply(lambda old_path: replace_base_path(old_path, st.session_state.BASE_PATH, 'json'))

                    # Determine SAVE_DIR from the 'path_to_content' column
                    first_path_to_content = st.session_state.data['path_to_content'][0]
                    parts = first_path_to_content.split(os.path.sep)
                    transcription_index = parts.index('Transcription') if 'Transcription' in parts else None
                    if transcription_index is not None:
                        create_save_dir(transcription_index)
                        # if len(parts[0]) == 2 and parts[0][1] == ":":
                            # parts[0] += os.path.sep
                        # st.session_state.SAVE_DIR = os.path.join(*parts[:transcription_index + 1])
                        # if not os.path.exists(st.session_state.SAVE_DIR):
                        #     os.makedirs(st.session_state.SAVE_DIR)

                    ######### Add new fields to the XLSX
                    if st.session_state.BASE_PATH_transcription_LLM == st.session_state.fullpath_working_file:
                        st.session_state.data = st.session_state.data.fillna('')

                        if "track_view" not in st.session_state.data.columns:
                            st.session_state.data["track_view"] = 'False'
                        if 'track_edit' not in st.session_state.data.columns:
                            st.session_state.data["track_edit"] = ["" for _ in range(len(st.session_state.data))]
                        if "track_issues" not in st.session_state.data.columns:
                            st.session_state.data["track_issues"] = 'False'
                        if "user_uniqname" not in st.session_state.data.columns:
                            st.session_state.data["user_uniqname"] = ""
                        if "user_time_of_edit" not in st.session_state.data.columns:
                            st.session_state.data["user_time_of_edit"] = ""

                        for group, columns in st.session_state.add_fields.items():
                            if 'filename' in st.session_state.data.columns:
                                filename_col_index = st.session_state.data.columns.get_loc('filename')
                                for col in columns:
                                    if col not in st.session_state.data.columns:
                                        st.session_state.data.insert(filename_col_index, col, [""] * len(st.session_state.data))
                                        filename_col_index += 1
                            else:
                                for col in columns:
                                    if col not in st.session_state.data.columns:
                                        st.session_state.data[col] = [""] * len(st.session_state.data)

                        # Create data_edited DataFrame
                        st.session_state.data_edited = pd.DataFrame(columns=st.session_state.data.columns)
                        st.session_state.data_edited['catalogNumber'] = st.session_state.data['catalogNumber']
                        st.session_state.data_edited['additionalText'] = st.session_state.data['additionalText']

                        # This is for the S/Drive craziness                     
                        # st.session_state.data_edited['path_to_crop'] = st.session_state.data['path_to_crop']
                        # st.session_state.data_edited['path_to_original'] = st.session_state.data['path_to_original']
                        # st.session_state.data_edited['path_to_helper'] = st.session_state.data['path_to_helper']
                        # st.session_state.data_edited['path_to_content'] = st.session_state.data['path_to_content']

                        always_keep_data_for = ['catalogNumber', 'additionalText']
                        always_keep_data_for = list(set(st.session_state.hide_fields + always_keep_data_for))

                        for col in st.session_state.data.columns:
                            if col == "country":
                                # Set all values to "" except where the value is "X" (case-insensitive)
                                st.session_state.data_edited[col] = st.session_state.data[col].str.strip().str.upper().where(
                                    st.session_state.data[col].str.strip().str.upper() == 'X', 
                                    other=''
                                )
                            elif col not in always_keep_data_for and st.session_state.data.columns.get_loc(col) < st.session_state.data.columns.get_loc('filename'):
                            # if col != 'catalogNumber' and col != 'additionalText' and st.session_state.data.columns.get_loc(col) < st.session_state.data.columns.get_loc('filename'):
                                st.session_state.data_edited[col] = [''] * len(st.session_state.data)
                            else:
                                # Retain the values for 'filename' and subsequent columns
                                st.session_state.data_edited[col] = st.session_state.data[col]

                    elif st.session_state.BASE_PATH_transcription_LLM_prior == st.session_state.fullpath_working_file:
                        raise ValueError("We only support editing files called 'transcribed.xlsx' and the '__edited__' files that result. If you want to look at 'transcribed_prior_to_subsetting.xlsx', then rename it to 'transcribed.xlsx'.")
                        
                    else:
                        st.session_state.data_edited = pd.read_excel(st.session_state.fullpath_working_file, dtype=str)
                        st.session_state.data_edited = st.session_state.data_edited.fillna('')
                        st.session_state.data = st.session_state.data.fillna('')
                        # st.session_state.data_edited = pd.DataFrame(columns=st.session_state.data.columns)
                        # If "track_edit" is present, update data_edited based on the presence of "track_edit"
                        for col in st.session_state.data_edited.columns:
                            # Update values where track_edit is not None
                            st.session_state.data_edited[col] = [
                                st.session_state.data_edited[col][i] if st.session_state.data_edited['track_edit'][i] is not None else st.session_state.data_edited[col][i]
                                for i in range(len(st.session_state.data_edited))
                            ]

                        # This is for the S/Drive craziness                     
                        st.session_state.data_edited['path_to_crop'] = st.session_state.data['path_to_crop'].apply(lambda old_path: replace_base_path(old_path, st.session_state.BASE_PATH, 'crop'))
                        st.session_state.data_edited['path_to_original'] = st.session_state.data['path_to_original'].apply(lambda old_path: replace_base_path(old_path, st.session_state.BASE_PATH, 'original'))
                        st.session_state.data_edited['path_to_helper'] = st.session_state.data['path_to_helper'].apply(lambda old_path: replace_base_path(old_path, st.session_state.BASE_PATH, 'jpg'))
                        st.session_state.data_edited['path_to_content'] = st.session_state.data['path_to_content'].apply(lambda old_path: replace_base_path(old_path, st.session_state.BASE_PATH, 'json'))

                        print(st.session_state.data_edited.head())
                        print(st.session_state.data_edited['path_to_crop'][0])
                        print(st.session_state.data_edited['path_to_original'][0])
                        print(st.session_state.data_edited['path_to_helper'][0])
                        print(st.session_state.data_edited['path_to_content'][0])


                        # for col in st.session_state.data.columns:
                        #     if col != 'catalogNumber':
                        #         st.session_state.data_edited[col] = [''] * len(st.session_state.data)
                    # print(st.session_state.data_edited.head())
                    # print('---DE empty')
                    # print(st.session_state.data_edited['genus'][2])
                    # print('---DE')
                    # print('---D full')
                    # print(st.session_state.data['genus'][2])
                    # print('---D\n')

                    # print('---DE full')
                    # print(st.session_state.data_edited['WFO_override_OCR'][2])
                    # print('---DE')
                    # print('---D full')
                    # print(st.session_state.data['WFO_override_OCR'][2])
                    # print('---D\n')

                    # print('---DE full')
                    # print(st.session_state.data_edited['filename'][2])
                    # print('---DE')
                    # print('---D full')
                    # print(st.session_state.data['filename'][2])
                    # print('---D\n')

                st.button("Start Editing", on_click=start_editing_btn, type="primary")

        
def start_editing_btn():
    st.session_state.start_editing = True
# def load_data(mapbox_key):
#     if 'data' not in st.session_state or st.session_state.data is None:
#         uploaded_file = st.file_uploader("Choose a CSV or Excel file", type=["csv", "xlsx"])
#     else:
#         uploaded_file = None

#     if uploaded_file is not None:
#         setup_streamlit_config(mapbox_key)

#         if uploaded_file.type == "text/csv":
#             data = pd.read_csv(uploaded_file, dtype=str)
#         elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":
#             data = pd.read_excel(uploaded_file, dtype=str)
#         st.session_state.n_columns = data.shape[1]

#         set_column_groups()

#         if "track_view" not in data.columns:
#             data["track_view"] = 'False'
#         if 'track_edit' not in data.columns:
#             data["track_edit"] = ["" for _ in range(len(data))]

#         st.session_state.data = data.fillna('')
#         file_extension = "csv" if uploaded_file.type == "text/csv" else "xlsx"
#         st.session_state.file_name = f"{uploaded_file.name.split('.')[0]}_edited.{file_extension}"

#         # If BASE_PATH is provided, replace old base paths in the dataframe
#         if st.session_state.BASE_PATH != '':
#             st.session_state.data['path_to_crop'] = st.session_state.data['path_to_crop'].apply(lambda old_path: replace_base_path(old_path, st.session_state.BASE_PATH, 'crop'))
#             st.session_state.data['path_to_original'] = st.session_state.data['path_to_original'].apply(lambda old_path: replace_base_path(old_path, st.session_state.BASE_PATH, 'original'))
#             st.session_state.data['path_to_helper'] = st.session_state.data['path_to_helper'].apply(lambda old_path: replace_base_path(old_path, st.session_state.BASE_PATH, 'jpg'))
#             st.session_state.data['path_to_content'] = st.session_state.data['path_to_content'].apply(lambda old_path: replace_base_path(old_path, st.session_state.BASE_PATH, 'json'))
        
#         # Determine SAVE_DIR from the 'path_to_content' column
#         first_path_to_content = st.session_state.data['path_to_content'][0]
#         print("")
#         print(first_path_to_content)
#         print("")
#         parts = first_path_to_content.split(os.path.sep)
#         transcription_index = parts.index('Transcription') if 'Transcription' in parts else None
#         print("")
#         print(parts)
#         print("")
#         if transcription_index is not None:
#             # add a slash after the drive letter if it is missing
#             if len(parts[0]) == 2 and parts[0][1] == ":":
#                 parts[0] += os.path.sep
#             st.session_state.SAVE_DIR = os.path.join(*parts[:transcription_index+1])
#             print(f"Saving edited file to {st.session_state.SAVE_DIR}")
#             if not os.path.exists(st.session_state.SAVE_DIR):
#                 print("UH OH! new dir created but it should not be")
#                 os.makedirs(st.session_state.SAVE_DIR)


def start_server():
    # Try to read the port from the file
    try:
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "settings", "streamlit_port.txt"), "r") as f:
            streamlit_port = int(f.read().strip())
    except:
        # Default port if file read fails
        streamlit_port = 8501
    
    st.session_state.http_server_port = streamlit_port - 1000
    print(f"Starting HTTP server for Zoom images on port {st.session_state.http_server_port}")

    current_dir = os.path.dirname(os.path.abspath(__file__))
        # Create the path to the new 'static' directory
    static_folder_path = os.path.join(current_dir, 'static')
        # Create 'static' directory
    os.makedirs(static_folder_path, exist_ok=True)
    # Ensure the server is run in a separate thread so it doesn't block the Streamlit app
    def target(http_server_port):
        subprocess.run(["python", "-m", "http.server", str(http_server_port)], cwd=static_folder_path, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    threading.Thread(target=target, args=(st.session_state.http_server_port,)).start()

    # Get the directory of the current file 
    st.session_state.current_dir = os.path.dirname(os.path.abspath(__file__))
    # Create the path to the new 'static' directory
    st.session_state.static_folder_path = os.path.join(st.session_state.current_dir, 'static')
    # Create 'static' directory
    os.makedirs(st.session_state.static_folder_path, exist_ok=True)
    st.session_state.static_folder_path_o = os.path.join(st.session_state.static_folder_path, "static_og")
    st.session_state.static_folder_path_c = os.path.join(st.session_state.static_folder_path, "static_cr")
    st.session_state.static_folder_path_h = os.path.join(st.session_state.static_folder_path, "static_h")
    os.makedirs(st.session_state.static_folder_path_o, exist_ok=True)
    os.makedirs(st.session_state.static_folder_path_c, exist_ok=True)
    os.makedirs(st.session_state.static_folder_path_h, exist_ok=True)

    logo_path = os.path.join(st.session_state.static_folder_path_c, 'logo.png')
    shutil.copy("img/logo.png", logo_path)

    relative_path_to_logo = os.path.relpath(logo_path, st.session_state.current_dir).replace('\\', '/')
    split_path = relative_path_to_logo.split('/')
    relative_path_to_logo = os.path.sep.join(split_path[1:])
    st.session_state.logo_path = relative_path_to_logo.replace('\\', '/')

def do_rerun():
    st.rerun()

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
    ################################################################################################################################################################### TEMP
    # st.session_state.BASE_PATH = "C:/Users/Will/Downloads/test_order"
    upload_and_unzip()

    # st.header("Instructions")
    # st.write("1. Provide the full path to where you want the edited transcription file to be saved. The default location is in the same folder as the un-edited transcription .xlsx file.")
    # st.write("2. Provide the full path to the folder that contains the VoucherVision transcription file.")
    # st.write("3. Select the prompt version that you used to create the transcription .xlsx file. Different prompts use different headers.")
    # st.write("4. (Optional) Provide a Mapbox API key. The free key-less version will suffice for most use-cases.")
    # st.write("5. Drag or browse for the transcription .xlsx file. Once this file is found, the editor will open.")
    # st.write("---")
    # # Get the save directory and base path from the parsed arguments or use the Streamlit input
    # # st.markdown("""#### Save Directory""")
    # # st.session_state.SAVE_DIR = args.save_dir if args.save_dir else st.text_input('Enter the directory to save output files', help=st.session_state.save_dir_help)
    # st.markdown("""#### Base Path""")
    # st.session_state.BASE_PATH = args.base_path if args.base_path else st.text_input('Include the full path to the folder that contains "/Transcription", but do not include "/Transcription" in the path', help=st.session_state.base_path_help)
    # st.markdown("""#### Prompt Version""")
    # st.session_state.prompt_version = args.prompt_version if args.prompt_version else st.radio('Prompt Version',options=['v2', 'v1'],help='Version 1 and Version 2 prompts have different column headers')

    # if 'Transcription' in st.session_state.BASE_PATH.split(os.path.sep):
    #     st.session_state.BASE_PATH = os.path.dirname(st.session_state.BASE_PATH)

    

def add_default_option_if_not_present():
    # Add default option if "track_edit" is empty and doesn't contain the default option already
    if group_options[0] not in st.session_state.data_edited.loc[st.session_state.row_to_edit, "track_edit"].split(","):
        if st.session_state.data_edited.loc[st.session_state.row_to_edit, "track_edit"]:
            st.session_state.data_edited.loc[st.session_state.row_to_edit, "track_edit"] += "," + group_options[0]
        else:
            st.session_state.data_edited.loc[st.session_state.row_to_edit, "track_edit"] = group_options[0]

###############################################################
#################      Progress Bars       ####################
###############################################################
def update_progress_bar():
    # Split the "track_edit" field into a list of options
    current_options = st.session_state.data_edited.loc[st.session_state.row_to_edit, "track_edit"].split(",")

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
    last_true_index = st.session_state.data_edited[st.session_state.data_edited["track_view"] == 'True'].index.max() + 1

    # Get total number of rows
    total_rows = len(st.session_state.data_edited)

    # Find the last row where "track_edit" has all group options
    last_full_view_index = st.session_state.data_edited[st.session_state.data_edited["track_edit"].apply(lambda x: set(group_options).issubset(set(x.split(','))))].index.max() + 1
    # Handle NaN last_full_view_index
    if pd.isnull(last_full_view_index):
        last_full_view_index = 0

    # Calculate the progress_overall as a fraction
    progress_overall_fraction = min(last_full_view_index / total_rows, 1.0)
    # print(progress_overall_fraction)
    # Display the progress_overall information
    # st.write(f"When 'Admin' is enabled, the following progress metrics will not update, but edits can still  be made.")

    # st.progress(progress_overall_fraction)
    # st.write(f"Viewed *{last_true_index}* of *{total_rows}* images")

    # st.write(f"Completed *{last_full_view_index}* of *{total_rows}* images")
    # Display the progress bar with text
    return last_true_index-1, last_full_view_index-1, progress_overall_fraction, total_rows



###############################################################
########################## Layouts ############################
###############################################################
def layout_image_proportion():
    """
    Set layout columns based on st.session_state.image_fill.
    
    Returns:
        tuple: (c_left, c_right) - The two columns created based on the image_fill state.
    """
    if st.session_state.image_fill == "Maximum - Image Right":
        c_left, c_right, c_help = st.columns([6, 9, 6])
    elif st.session_state.image_fill == "More - Image Right":
        c_left, c_right, c_help = st.columns([6, 9, 4])
    elif st.session_state.image_fill == "Balanced - Image Right":
        c_left, c_right, c_help = st.columns([8, 8, 3])

    elif st.session_state.image_fill == "Maximum - Image Left":
        c_right, c_left, c_help = st.columns([9, 6, 6])
    elif st.session_state.image_fill == "More - Image Left":
        c_right, c_left, c_help = st.columns([9, 6, 4])
    elif st.session_state.image_fill == "Balanced - Image Left":
        c_right, c_left, c_help = st.columns([8, 8, 3])
    elif st.session_state.image_fill == "Small Screen":
        c_left, c_right = st.columns([8, 8])
        c_help = None
    else:
        c_left, c_right, c_help = st.columns([8, 8, 3])
    
    return c_left, c_right, c_help

@st.cache_data
def show_header_welcome():
    # Create three columns
    h1, h2, h3 = st.columns([2,1,2])
    # Use the second (middle) column for the logo
    with h2:
        # st.image("img/logo.png", use_container_width=True)
        st.markdown(f'<a href="https://github.com/Gene-Weaver/VoucherVisionEditor"><img src="http://localhost:{st.session_state.http_server_port}/{st.session_state.logo_path}" width="200"></a>', unsafe_allow_html=True)
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
            st.image(f"http://localhost:{st.session_state.http_server_port}/{st.session_state.logo_path}", use_container_width=True)
            # st.markdown("<h1 style='text-align: center;'>VoucherVision Editor</h1>", unsafe_allow_html=True)
            # Use the first column for the logo and the second for the title
            # st.image("img/logo.png", width=200)  # adjust width as needed
            # st.markdown(f'<a href="https://github.com/Gene-Weaver/VoucherVisionEditor"><img src="http://localhost:8000/{st.session_state.logo_path}" width="100"></a>', unsafe_allow_html=True)
        
            st.markdown(f"<h2 style='text-align: center;'><a href='https://forms.gle/kP8imC9JQTPLrXgg8' target='_blank'>Report a Bug</a></h2>", unsafe_allow_html=True)

        st.session_state.default_to_original = st.sidebar.checkbox("Default to Original image each time 'Next' or 'Previous' is pressed.", value=True)  

        # Image Layout Focus selectbox
        st.session_state.image_fill = st.sidebar.selectbox("Image Layout Focus", ["More - Image Right", "Balanced - Image Right",  "Maximum - Image Right",
                                                                                  "Small Screen",
                                                                                  "More - Image Left", "Balanced - Image Left", "Maximum - Image Left",])

        # Image Size selectbox
        st.session_state.set_image_size = st.sidebar.selectbox("Image Size", ["Custom", "Medium", "Large", "Small", "Auto Width", "Fitted"])

        # Set Image Width slider
        if st.session_state.set_image_size == "Custom":
            image_sizes = list(range(200, 2601, 50))
            st.session_state.set_image_size_px = st.select_slider('Set Image Width', options=image_sizes, value=st.session_state.set_image_size_px)

        # Set Viewing Height slider
        if st.session_state.set_image_size != "Auto Width":
            image_sizes = list(range(20, 401, 5))
            st.session_state.set_image_size_pxh = st.select_slider('Set Viewing Height', options=image_sizes, value=st.session_state.set_image_size_pxh)

        # Set Map Height slider
        if st.session_state.set_map_height:
            image_sizes = list(range(50, 501, 10))
            st.session_state.set_map_height_pxh = st.select_slider('Set Map Height', options=image_sizes, value=st.session_state.set_map_height_pxh)

        wrap_len = list(range(10, 101, 1))
        st.session_state.form_width = st.select_slider('Text wrapping length for form values', options=wrap_len, value=20)
        # Location of the form record TRUTH

        st.session_state.color_table_viewed = st.color_picker("Color of Viewed Records in the Table", "#009ec4")
        st.session_state.color_table_issue = st.color_picker("Color of Bookmarked Records in the Table", "#F08080")
        st.session_state.color_table_ignored = st.color_picker("Color of Ignored Records in the Table", "#000000")

        # Location of the Google Search
        if st.session_state.image_fill == "Small Screen":
            st.session_state.location_google_search = st.sidebar.selectbox("Location of Google Search - Small Screen", ["Top", "Bottom"])
        else:
            st.session_state.location_google_search = st.sidebar.selectbox("Location of Google Search", ["Top", "Hint Panel", "Bottom"])
        
        st.session_state.google_search_new_window = st.sidebar.checkbox("Open Google search in new browser tab", value=st.session_state.google_search_new_window)

        st.session_state.tool_access['show_skip_specimen'] = st.sidebar.checkbox("Show the 'skip specimen' button", value=st.session_state.tool_access['show_skip_specimen'])

        ######## Additional Options ################
        st.sidebar.header('Options') #,help='Visible as Admin')

        # Access selectbox
        user_pwd = st.text_input("Admin Password", type="password",help="use: vouchervisionadmin")
        if user_pwd == st.session_state.pwd:
            st.session_state.access_option = st.sidebar.selectbox("Access", ["Labeler", "Admin"])
        else:
            st.session_state.access_option = st.sidebar.selectbox("Access", ["Labeler", "Admin"], disabled=True)

        if st.session_state.access_option in ["Admin",] and user_pwd == st.session_state.pwd:
            st.session_state.form_hint_location = st.sidebar.selectbox("Position of the form hints", ["Left", "Right"])
            # Warning message for 
            distances_GPS = list(range(0, 501, 10))
            st.session_state.distance_GPS_warn = st.select_slider('Display warning message if Verbarim/Decimal coordinates disagree by more than X km.', options=distances_GPS, value=100)

            st.session_state.tool_access['hints'] = st.checkbox("Display WFO and GEO form hints",value=st.session_state.tool_access.get('hints'))
            if not st.session_state.tool_access['hints']:
                st.session_state.tool_access['arrow'] = False
                # st.session_state.form_width = st.session_state.form_width_2
                st.session_state.tool_access['arrow'] = st.checkbox("Display move arrow button for form hints :arrow_forward:",value=st.session_state.tool_access.get('hints'),disabled=True)
            else:
                # st.session_state.form_width = st.session_state.form_width_1
                st.session_state.tool_access['arrow'] = st.checkbox("Display move arrow button for form hints :arrow_forward:",value=st.session_state.tool_access.get('arrow'),disabled=False)

            st.session_state.tool_access['show_skip_specimen'] = st.checkbox("Display button to skip specimen and add it to transcribed_skipped.xlsx",value=st.session_state.tool_access.get('show_skip_specimen'))
            st.session_state.tool_access['ocr'] = st.checkbox("Display button to view OCR image",value=st.session_state.tool_access.get('ocr'))
            st.session_state.tool_access['wfo_badge'] = st.checkbox("Display WFO badge",value=st.session_state.tool_access.get('wfo_badge'))
            st.session_state.tool_access['taxa_links'] = st.checkbox("Display buttons for Wikipedia (taxonomy), POWO, GRIN",value=st.session_state.tool_access.get('taxa_links'))
            st.session_state.tool_access['wfo_links'] = st.checkbox("Display top 10 list of WFO taxa (WFO partial matches)",value=st.session_state.tool_access.get('wfo_links'))
            st.session_state.tool_access['additional_info'] = st.checkbox("Display additional project information at page bottom",value=st.session_state.tool_access.get('additional_info'))
            st.session_state.tool_access['cap'] = st.checkbox("Display capitalization buttons :eject: and :arrow_double_down:",value=st.session_state.tool_access.get('cap'))
            st.session_state.tool_access['search'] = st.checkbox("Display quick search buttons :mag:",value=st.session_state.tool_access.get('search'))
       
            # # Choose a View selectbox
            # st.session_state.view_option = st.sidebar.selectbox("Choose a View", ["Form View", "Data Editor"], disabled=True)

            # # Store previous image size
            # st.session_state.set_image_size_previous = st.session_state.set_image_size

            # st.session_state.use_extra_image_options = st.sidebar.checkbox("Include toggle for fitted image view.", value=False)
            # if st.session_state.use_extra_image_options:
            #     image_sizes_fitted = list(range(100, 1201, 50))
            #     st.session_state.set_image_size_px = st.select_slider(
            #         'Set Fitted Image Width',
            #         options=image_sizes_fitted,value=600)
            
            # # fitted_image_width
            
        else:
            st.session_state.access_option = "Labeler"
        


###############################################################
###################### Load Files #############################
###############################################################
def load_json_helper_files():
    """
    Load related JSON files based on the current row being edited. 
    Updates the st.session_state with 'json_dict' for the helper JSON and 'OCR_JSON' for the OCR data.
    """
    try:
        if st.session_state['last_row_to_edit'] != st.session_state.row_to_edit:
            JSON_path = st.session_state.data_edited.loc[st.session_state.row_to_edit, "path_to_content"]

            if JSON_path:
                with open(JSON_path, "r") as file:
                    st.session_state['json_dict'] = json.load(file)
            else:
                print(f"Error loading LLM JSON file from PROJECT/Transcription/Individual/...json {JSON_path}: st.session_state['json_dict'] = json.load(file)")
                st.session_state['json_dict'] = {}

            # Load second JSON (OCR)
            original_JSON_path = st.session_state.data_edited.loc[st.session_state.row_to_edit, "path_to_content"]
            
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
            else:
                print(f"Error loading OCR_JSON file from PROJECT/Transcription/Individual_OCR/...json --- {JSON_path} --- st.session_state['OCR_JSON'] = json.load(file)")
                st.session_state['OCR_JSON'] = {}
    except Exception as e:
        print(e)
        st.session_state['json_dict'] = {}
        st.session_state['OCR_JSON'] = {}


###############################################################
####################### Button Press ##########################
###############################################################
def on_press_skip_specimen():
    st.session_state.data_edited.loc[st.session_state.row_to_edit, "country"] = "X"
    st.session_state.data_edited.loc[st.session_state.row_to_edit, "track_view"] = 'True'

    new_skipped_data = st.session_state.data.loc[[st.session_state.row_to_edit]]
    print(new_skipped_data)
    save_data_skipped(new_skipped_data)

    group_options = list(st.session_state.grouping.keys()) + ["ALL"]
    finished_options = group_options[0]
    for option in group_options[1:]:
        finished_options += "," + option
    st.session_state.data_edited.loc[st.session_state.row_to_edit, "track_edit"] = finished_options
    save_data()


def on_press_previous():
    """
    Handle actions when the "Previous" button is pressed.
    """
    st.session_state.progress_counter = 0
    if st.session_state.current_options:
        # Store current options as a list in "track_edit" column
        st.session_state.data_edited.loc[st.session_state.row_to_edit, "track_edit"] = st.session_state.current_options
    # Add default option if "track_edit" is empty and doesn't contain the default option already
    add_default_option_if_not_present()

    if st.session_state.row_to_edit == st.session_state.data_edited.index[0]:
        if st.session_state.access_option == 'Admin':
            st.session_state.row_to_edit = st.session_state.data_edited.index[-1]
    else:
        st.session_state.row_to_edit -= 1
        while st.session_state.row_to_edit in st.session_state.data_edited.index and \
            st.session_state.data.loc[st.session_state.row_to_edit, 'country'].strip().lower() == 'x':
            st.session_state.row_to_edit -= 1

    # st.session_state["group_option"] = group_options[0]  # Reset the group_option
    if st.session_state.default_to_original:
        st.session_state.image_option = 'Original'

def on_press_next(group_options):
    """
    Handle actions when the "Next" button is pressed.
    """
    # Init tracker
    for i, option in enumerate(group_options):
        st.session_state.group_options_tracker[option] = 0

    if st.session_state.progress >= len(group_options) or st.session_state.access_option == 'Admin':
        if st.session_state.data_edited.loc[st.session_state.row_to_edit, "user_time_of_edit"] == "":
            st.session_state.data_edited.loc[st.session_state.row_to_edit, "user_time_of_edit"] = get_current_datetime()
            save_data()

        st.session_state.progress_counter = 0
        st.session_state.progress_index = 0
        if st.session_state.current_options:
            # Store current options as a list in "track_edit" column
            st.session_state.data_edited.loc[st.session_state.row_to_edit, "track_edit"] = st.session_state.current_options
        # Add default option if "track_edit" is empty and doesn't contain the default option already
        add_default_option_if_not_present()

        if st.session_state.row_to_edit == st.session_state.data_edited.index[-1]:
            st.session_state.row_to_edit = st.session_state.data_edited.index[0]
            st.balloons()
        else:
            st.session_state.row_to_edit += 1
            print(st.session_state.data.loc[st.session_state.row_to_edit, 'country'].strip().lower())
            # **Skip rows where 'country' is 'X' or 'x'**
            while st.session_state.row_to_edit in st.session_state.data_edited.index and \
                  st.session_state.data.loc[st.session_state.row_to_edit, 'country'].strip().lower() == 'x':
                if st.session_state.row_to_edit == st.session_state.data_edited.index[-1]:
                    st.session_state.row_to_edit = st.session_state.data_edited.index[0]  # Loop back to start
                else:
                    st.session_state.data_edited.loc[st.session_state.row_to_edit, 'track_view'] = 'True'
                    st.session_state.data_edited.loc[st.session_state.row_to_edit, 'country'] = 'X'
                    for option in group_options:
                        current_edit_track = st.session_state.data_edited.loc[st.session_state.row_to_edit, "track_edit"]
                        if option not in current_edit_track.split(","):
                            new_edit_track = current_edit_track + "," + option if current_edit_track else option
                            st.session_state.data_edited.loc[st.session_state.row_to_edit, "track_edit"] = new_edit_track
                    st.session_state.row_to_edit += 1

        st.session_state["group_option"] = group_options[0]  # Reset the group_option
        if st.session_state.default_to_original:
            st.session_state.image_option = 'Original'
    else:
        pass
        # st.info("Please confirm all categories before moving to next image")

def on_press_skip_to_bookmark():
    last_true_index, last_fully_viewed, progress_overall_fraction, total_rows = update_progress_bar_overall()
    st.session_state.row_to_edit = int(last_true_index)

def on_press_confirm_content(group_option, group_options):
    print(st.session_state.group_options_tracker)

    # Check if the current group_option is unlocked (1) and ensure the next group_option is locked (0).
    if (
        st.session_state.group_options_tracker[group_option] == 0
        and st.session_state.progress_index < len(group_options)
        and st.session_state.group_options_tracker[group_options[st.session_state.progress_index]] == 0
    ):
        # Advance the progress index
        st.session_state.progress_index += 1
        # Mark the current group_option as processed
        st.session_state.group_options_tracker[group_option] = 1

    # Iterate through group options to determine which button to enable
    for i, option in enumerate(group_options):
        if i == st.session_state.progress_index:
            st.session_state["group_option"] = option
            group_option = option

            if "track_edit" not in st.session_state.data_edited.columns:
                st.session_state.data_edited["track_edit"] = [
                    [group_options[0]] if group_options[0] else [] for _ in range(len(st.session_state.data_edited))
                ]

            # Update the "track_edit" column only for non-admin users
            if st.session_state.access_option != "Admin":
                current_edit_track = st.session_state.data_edited.loc[st.session_state.row_to_edit, "track_edit"]
                if option not in current_edit_track.split(","):
                    new_edit_track = current_edit_track + "," + option if current_edit_track else option
                    st.session_state.data_edited.loc[st.session_state.row_to_edit, "track_edit"] = new_edit_track

                    # Add the default option if not present
                    add_default_option_if_not_present()

    # Clear helper input keys
    for col in st.session_state.prompt_mapping:
        helper_input_key = f"helper_{col}"
        st.session_state[helper_input_key] = None


    save_data()

###############################################################
###################### Display Table ##########################
###############################################################
def calculate_table_height(entries_per_page, base_height=420):
    """Calculate table height dynamically based on entries per page."""
    return base_height * (entries_per_page // 10)

def style_dataframe_with_issues(df):
    """
    Apply Pandas Styler to highlight rows with multiple rules for 'track_issues', 'country', and 'track_view'.
    """
    # Ensure the index is unique
    df = df.reset_index(drop=True)

    def highlight_issues(row):
        """Highlight the row if 'track_issues' is True."""
        styles = [''] * len(row)
        if row.get("track_issues") == "True":  # Use .get() to avoid key errors
            print(f'background-color: #{st.session_state.color_table_issue}')
            styles = [f'background-color: {st.session_state.color_table_issue}' for _ in row]
        return styles

    def highlight_x(row):
        """Highlight the row if 'country' is 'X'."""
        styles = [''] * len(row)
        if row.get("country") == "X":  # Use .get() to avoid key errors
            for i in range(len(styles)):
                styles[i] += f'background-color: {st.session_state.color_table_ignored};'
        return styles
    def highlight_viewed(row):
        """Highlight the row if 'track_view' is True."""
        styles = [''] * len(row)
        if row.get("track_view") == "True":  # Use .get() to avoid key errors
            for i in range(len(styles)):
                styles[i] += f'background-color: {st.session_state.color_table_viewed};'
        return styles

    # Apply the styling to the DataFrame
    styled_df = df.style.apply(
        lambda row: [
            f"{issue}{x}{finished}" 
            for issue, x, finished in zip(
                highlight_x(row), 
                highlight_viewed(row),
                highlight_issues(row), 
            )
        ], 
        axis=1
    )

    return styled_df



def highlight_text_in_table(table, text_query, entries_per_page, DIS_CLASSES):
    """
    Highlight the text_query in the table by wrapping it with a <span> that has red color.
    """
    # JavaScript logic to highlight the query in red
    highlight_js = JavascriptCode(f"""
    function(data, type, row, meta) {{
        if (typeof data === 'string') {{
            return data.replace(new RegExp("({text_query})", "gi"), '<span style="color:red">$1</span>');
        }}
        return data;
    }}
    """)

    # Apply the highlight function to all columns using columnDefs
    column_defs = [{"targets": "_all", "render": highlight_js}]
    
    return to_html_datatable(table, classes="display nowrap compact cell-border", columnDefs=column_defs, lengthMenu=[entries_per_page])



def table_layout(t_location):
    st.title('')
    current_project_name = os.path.basename(os.path.dirname(os.path.dirname(os.path.join(st.session_state.SAVE_DIR, st.session_state.file_name))))
    st.markdown(f"**Current Project:** :green[{current_project_name}]", help="This is the name of the current project")
    st.markdown(f"**Current Transcription File:** :green[{st.session_state.file_name}]", help="This is the name of the transcribed_edited__DATETTIME.xlsx file")
    st.markdown(f"**Total Number of Images in Project:** :green[{st.session_state.n_total_data}]", help="Number of images in the whole project, includes images that are outside the current geographic bounds.")
    st.markdown(f"**Number of Images to Review:** :green[{st.session_state.n_manual_data}]", help="Number of images that you will actually edit that fall within the geographic bounds of this project")

    DIS_CLASSES = "display nowrap compact cell-border"

    c_entries, c_entries_2 = st.columns([2,10])
    with c_entries:
        entries_per_page = st.selectbox('Entries per page:', [10, 20, 50, 100], index=2,key=f'Entries per page{t_location}')  # Default is 10
    if entries_per_page is None:
        entries_per_page = 10

    table_height = calculate_table_height(entries_per_page)
    if st.session_state.table_height_holder != table_height:
        st.session_state.table_height_holder = table_height
        st.rerun()

    table = st.session_state.data_edited

    # Add the index as a column, increment it by 1, and name it 'Index'
    table = table.reset_index(drop=True)
    table.index = table.index + 1
    table['Img'] = table.index

    # Reorder columns to show 'Index' first
    cols = ['Img'] + [col for col in table.columns if col not in ['Img', 'Index']]
    table = table[cols]

    # Get text query from user input
    text_query = "Carex"
    # duplicate_columns = [col for col in table.columns if list(table.columns).count(col) > 1]
    # print(duplicate_columns)

    assert table.columns.is_unique, "DataFrame has non-unique column names."

    table = style_dataframe_with_issues(table)

    # Highlight the query in the table
    if text_query:
        table_html = highlight_text_in_table(table, text_query, entries_per_page, DIS_CLASSES)
    else:
        table_html = to_html_datatable(table, classes=DIS_CLASSES, lengthMenu=[entries_per_page])

    # Render the table with custom CSS and dynamic height
    html(HelpText.TABLECSS + table_html, height=table_height)


#########   https://mwouts.github.io/itables/formatting.html








###############################################################
################# Display Rows in the Form ####################
############################################################### 
# def form_layout(group_option, grouping):
#     """
#     Display form layout based on group_option and update st.session_state.data.

#     Parameters:
#         group_option (str): Current group option.
#         grouping (dict): Dictionary mapping groups to fields.
#         color_map (dict): Dictionary mapping groups to colors.
#     """
#     columns_to_show = st.session_state.data.columns if group_option == "ALL" else st.session_state.grouping[group_option]
#     for col in columns_to_show:
#         if col not in ['track_view', 'track_edit']:
#             # Find the corresponding group and color
#             unique_key = f"{st.session_state.row_to_edit}_{col}"
#             for group, fields in st.session_state.grouping.items():
#                 if col in fields:
#                     color = st.session_state.color_map.get(group, "#FFFFFF")  # default to white color
#                     break
#             else:
#                 color = st.session_state.color_map.get("MISCELLANEOUS", "#FFFFFF")  # default to white color

#             colored_label = f":{color}[{col}]"

#             # IF admin, allow barcode to be edited
#             if (st.session_state.access_option == 'Admin' and (col in ['catalogNumber',])): 
#                 # Show editable catalog number to admin
#                 st.session_state.user_input[col] = st.text_input(colored_label, st.session_state.data.loc[st.session_state.row_to_edit, col], key=unique_key,)
#             elif (st.session_state.access_option == 'Labeler' and (col in ['catalogNumber',])): 
#                 # Show disabled catalog number to labeler
#                 st.session_state.user_input[col] = st.text_input(colored_label, st.session_state.data.loc[st.session_state.row_to_edit, col], key=unique_key, disabled=True)
#             else:
#                 if len(st.session_state.data.loc[st.session_state.row_to_edit, col]) > st.session_state.form_width:
#                     st.session_state.user_input[col] = st.text_area(colored_label, st.session_state.data.loc[st.session_state.row_to_edit, col], key=unique_key)
#                 else:
#                     st.session_state.user_input[col] = st.text_input(colored_label, st.session_state.data.loc[st.session_state.row_to_edit, col], key=unique_key)
#             if st.session_state.user_input[col] != st.session_state.data.loc[st.session_state.row_to_edit, col]:
#                 st.session_state.data.loc[st.session_state.row_to_edit, col] = st.session_state.user_input[col]
#                 save_data()

# Define the helper map outside of the functions
helper_map = {
    "country": "GEO_country",
    "stateProvince": "GEO_state",
    "county": "GEO_county",
    "municipality": "GEO_city",
    "decimalLatitude": "GEO_decimal_lat",
    "decimalLongitude": "GEO_decimal_long",

    "order": "WFO_placement", #WFO_placement[3]
    "family": "WFO_placement", #WFO_placement[4]
    "scientificName": "WFO_best_match",  #WFO_best_match[0][1]
    "scientificNameAuthorship": "WFO_best_match",  #WFO_best_match[2:] ################################################################################################ NEEDS TO BE A CONFIG
    "genus": "WFO_placement", #WFO_placement[5]
    "specificEpithet": "WFO_placement", #WFO_placement[6]
}
    
#########################################################################################################################################################################################
#########################################################################################################################################################################################
#########################################################################################################################################################################################
def display_issue_badge():
    col_thumb, col_thumb_badge = st.columns([0.2, 0.8])
    
    # if st.session_state.tool_access.get('wfo_badge'):
    # st.session_state.wfo_match_level = "No Match"
    # is_exact_match = st.session_state.data_edited['WFO_exact_match'][st.session_state.row_to_edit]
    # if is_exact_match == 'True':
    #     hint = ("World Flora Online", "Exact Match", "#059c1b")  # Red for invalid
    #     st.session_state.wfo_match_level = "Exact Match"
    # else:
    #     is_best_match = st.session_state.data_edited['WFO_best_match'][st.session_state.row_to_edit]
    #     if len(is_best_match) > 0:
    #         hint = ("World Flora Online", "Partial Match", "#0252c9")  # Red for invalid
    #         st.session_state.wfo_match_level =  "Partial Match"
    #     else:
    #         hint = ("World Flora Online", "No Match", "#870307")  # Red for invalid
    sentiment_mapping = ["ISSUE", "OKAY"]

    with col_thumb:
        # Manually set the preselected value based on the current "track_issues" value
        if st.session_state.data_edited.loc[st.session_state.row_to_edit, "track_issues"] == 'True':
            preselected = 0  # ISSUE (Thumbs down)
        else:
            preselected = 1  # OKAY (Thumbs up)

        # Get user feedback, or fall back to preselected if no selection is made
        selected = st.feedback("thumbs", key=f"issue_id_thumb{int(st.session_state.row_to_edit)}")

        # If no selection is made, use the preselected value
        if selected is None:
            selected = preselected

        # Update "track_issues" and the hint based on the selected feedback
        if sentiment_mapping[selected] == "ISSUE":
            # If ISSUE is selected, flag the row and set the hint
            hint = ("ISSUE", "This specimen has been flagged", "#870307")  # Red for invalid
            st.session_state.data_edited.loc[st.session_state.row_to_edit, "track_issues"] = 'True'
            save_data()
        else:
            # If OKAY is selected, unflag the row and remove the hint
            st.session_state.data_edited.loc[st.session_state.row_to_edit, "track_issues"] = 'False'
            hint = None
            save_data()

    with col_thumb_badge:
        if hint:
            annotated_text(hint)



def display_wfo_badge():
    if st.session_state.tool_access.get('wfo_badge'):
        st.session_state.wfo_match_level = "No Match"
        is_exact_match = st.session_state.data_edited['WFO_exact_match'][st.session_state.row_to_edit]
        if is_exact_match == 'True':
            hint = ("World Flora Online", "Exact Match", "#059c1b")  # Red for invalid
            st.session_state.wfo_match_level = "Exact Match"
        else:
            is_best_match = st.session_state.data_edited['WFO_best_match'][st.session_state.row_to_edit]
            if len(is_best_match) > 0:
                hint = ("World Flora Online", "Partial Match", "#0252c9")  # Red for invalid
                st.session_state.wfo_match_level =  "Partial Match"
            else:
                hint = ("World Flora Online", "No Match", "#870307")  # Red for invalid

        if hint:    
            annotated_text(hint)

@contextmanager
def noop_context():
    yield None

def get_move_format():
    # Initialize the move_format list
    move_format = []
    c_help = noop_context()  # Use noop_context as the default
    c_move = noop_context()
    c_form = noop_context()
    c_cap = noop_context()
    c_lower = noop_context()
    c_search = noop_context()

    if not st.session_state.tool_access.get('hints'):
        st.session_state.tool_access['arrow'] = False
    
    # Check each condition and modify move_format accordingly
    if st.session_state.tool_access.get('hints'):
        move_format.extend([6])  # Adjust these values as needed

    
    if st.session_state.tool_access.get('arrow'):
        move_format.extend([1])  

    if st.session_state.tool_access.get('form'): # ALWAYS TRUE
        move_format.extend([6])  # MAIN FORM
    
    if st.session_state.tool_access.get('cap'):
        move_format.extend([1])  
        move_format.extend([1])  
    
    if st.session_state.tool_access.get('search'):
        move_format.extend([1])  
    
    # Default case if none of the above conditions are met, adjust as necessary
    # if not move_format:
    #     move_format = [10, 1, 1, 1]  # Default format
        
    if (not st.session_state.tool_access.get('hints') 
        and not st.session_state.tool_access.get('arrow') 
        and not st.session_state.tool_access.get('cap')
        and not st.session_state.tool_access.get('search')):
        c_form = st.columns([1])
    elif (st.session_state.tool_access.get('hints') 
        and not st.session_state.tool_access.get('arrow') 
        and not st.session_state.tool_access.get('cap')
        and not st.session_state.tool_access.get('search')):
        c_help, c_form = st.columns(move_format)
    elif (st.session_state.tool_access.get('hints') 
        and st.session_state.tool_access.get('arrow') 
        and not st.session_state.tool_access.get('cap')
        and not st.session_state.tool_access.get('search')):
        c_help, c_move, c_form = st.columns(move_format)
    elif (st.session_state.tool_access.get('hints') 
        and st.session_state.tool_access.get('arrow') 
        and st.session_state.tool_access.get('cap')
        and not st.session_state.tool_access.get('search')):
        c_help, c_move, c_form, c_cap, c_lower = st.columns(move_format)
    elif (st.session_state.tool_access.get('hints') 
        and st.session_state.tool_access.get('arrow') 
        and st.session_state.tool_access.get('cap')
        and st.session_state.tool_access.get('search')):
        c_help, c_move, c_form, c_cap, c_lower, c_search = st.columns(move_format)
    elif (st.session_state.tool_access.get('hints') 
        and not st.session_state.tool_access.get('arrow') 
        and st.session_state.tool_access.get('cap')
        and not st.session_state.tool_access.get('search')):
        c_help, c_form, c_cap, c_lower = st.columns(move_format)
    elif (st.session_state.tool_access.get('hints') 
        and not st.session_state.tool_access.get('arrow') 
        and st.session_state.tool_access.get('cap')
        and st.session_state.tool_access.get('search')):
        c_help, c_form, c_cap, c_lower, c_search = st.columns(move_format)
    elif (st.session_state.tool_access.get('hints') 
        and st.session_state.tool_access.get('arrow') 
        and not st.session_state.tool_access.get('cap')
        and st.session_state.tool_access.get('search')):
        c_help, c_move, c_form, c_search = st.columns(move_format)
    elif (not st.session_state.tool_access.get('hints') 
        and st.session_state.tool_access.get('cap')
        and st.session_state.tool_access.get('search')):
        c_form, c_cap, c_lower, c_search = st.columns(move_format)
    elif (not st.session_state.tool_access.get('hints') 
        and not st.session_state.tool_access.get('cap')
        and st.session_state.tool_access.get('search')):
        c_form, c_search = st.columns(move_format)
    elif (not st.session_state.tool_access.get('hints') 
        and st.session_state.tool_access.get('cap')
        and not st.session_state.tool_access.get('search')):
        c_form, c_cap, c_lower,  = st.columns(move_format)
    else:
        move_format = [6]
        c_form  = st.columns(move_format)

    if isinstance(c_form, list):
        c_form = c_form[0]

    
    return move_format, c_help, c_move, c_form, c_cap, c_lower, c_search

def display_layout_with_helpers(group_option):
    display_issue_badge()
    # display_wfo_badge()

    # if ( st.session_state.tool_access.get('arrow') and 
    #         st.session_state.tool_access.get('hints') and
    #         st.session_state.tool_access.get('cap') and
    #         st.session_state.tool_access.get('search')
    # ):
    #     move_format = [6, 1, 6, 1, 1, 1]
    # elif (not st.session_state.tool_access.get('arrow') and 
    #         st.session_state.tool_access.get('hints') and 
    #         st.session_state.tool_access.get('cap') and
    #         st.session_state.tool_access.get('search')
    # ):
    #     move_format = [6, 6, 1, 1, 1]
    # else:
    #     move_format = [10, 1, 1, 1]

    i = 0
    
    for col in get_columns_to_show(group_option):
        if col not in st.session_state.hide_columns_in_editor:
            i += 1
            with st.container():
                if st.session_state.tool_access.get('arrow') and st.session_state.tool_access.get('hints'):
                    if st.session_state.form_hint_location == 'Left':
                        # c_help, c_move, c_form, c_cap, c_lower, c_search = st.columns(move_format)
                        move_format, c_help, c_move, c_form, c_cap, c_lower, c_search = get_move_format()
                        # move_arrow = "==:arrow_forward:"
                        move_arrow = ":arrow_forward:"
                    elif st.session_state.form_hint_location == 'Right':
                        # c_form, c_move, c_help, c_cap, c_lower, c_search = st.columns(move_format)
                        move_format, c_form, c_move, c_help, c_cap, c_lower, c_search = get_move_format()
                        # move_arrow = ":arrow_backward:=="
                        move_arrow = ":arrow_backward:"

                    else:
                        move_format, c_help, c_move, c_form, c_cap, c_lower, c_search = get_move_format()

                else:
                    # if st.session_state.tool_access.get('hints'):
                    #     c_help, c_form, c_cap, c_lower, c_search = st.columns(move_format)
                    # else:
                    #     c_form, c_cap, c_lower, c_search = st.columns(move_format)
                    move_format, c_help, c_move, c_form, c_cap, c_lower, c_search = get_move_format()



                if i == 1:
                    if st.session_state.tool_access.get('form'):
                        with c_form:
                            st.markdown(f"<u><b>Specimen Record</b></u>", unsafe_allow_html=True)
                    if st.session_state.tool_access.get('arrow') and st.session_state.tool_access.get('hints'):
                        with c_move:
                            st.markdown(move_arrow)
                    if st.session_state.tool_access.get('hints'):
                        with c_help:
                            st.text("AI Text")
                    if st.session_state.tool_access.get('cap'):
                        with c_cap:
                            st.text("Cap")
                        with c_lower:
                            st.text("Low")
                    if st.session_state.tool_access.get('search'):
                        with c_search:
                            st.text("Web")
                form_layout(group_option,col, c_form)
                # display_move_button(col, c_move, move_arrow=move_arrow)
                if st.session_state.tool_access.get('cap'):
                    display_cap_case_button(col, c_cap)
                    display_lower_case_button(col, c_lower)
                if st.session_state.tool_access.get('search'):
                    display_search_button(col, c_search)
                if st.session_state.tool_access.get('arrow') and st.session_state.tool_access.get('hints'):
                    display_LLM_input(col, c_help, c_move=c_move, move_arrow=move_arrow)
                    # display_helper_input(col, c_help, c_move=c_move, move_arrow=move_arrow)
                elif not st.session_state.tool_access.get('arrow') and st.session_state.tool_access.get('hints'):
                    display_LLM_input(col, c_help, c_move=None, move_arrow=None)
                    # display_helper_input(col, c_help, c_move=None, move_arrow=None)
                else:
                    display_LLM_input(col, c_help=None, c_move=None, move_arrow=None)
                    # display_helper_input(col, c_help=None, c_move=None, move_arrow=None)


    
    st.button('Unlock Next Category :unlock:',key=f"Confirm_Content_{group_option}", use_container_width=True, type="primary",on_click=on_press_confirm_content,args=[group_option, group_options]) 



def form_layout(group_option, col, c_form):
    with c_form:
        # Determine columns to show
        if (col not in ['user_uniqname', 'user_time_of_edit', 'track_view', 'track_edit', 'track_issues']) and (col not in st.session_state.hide_fields):
            unique_key, color = prepare_column(col)
            handle_column_input(col, unique_key, color)


def display_LLM_input(col, c_help, c_move, move_arrow):
    if 'data' in st.session_state:
        LLM_input_key = f"LLM_{col}"

        # Check if the column should be displayed
        if col in st.session_state.hide_fields:  # Adjust condition based on your requirements
            return

        # Get the suggested value directly from the data DataFrame
        if col in st.session_state.data.columns:
            suggested_value = str(st.session_state.data[col][st.session_state.row_to_edit]) if st.session_state.row_to_edit < len(st.session_state.data) else ''
        else:
            suggested_value = ''

        # Initialize the session state variable before widget creation
        if LLM_input_key not in st.session_state:
            st.session_state[LLM_input_key] = suggested_value

        # Initialize the session state variable before widget creation
        if LLM_input_key not in st.session_state:
            st.session_state[LLM_input_key] = suggested_value

        # Display the input field
        with c_help:

            input_type = determine_input_type(col,suggested_value)
            
            input_type(f"{col} (LLM)", suggested_value, key=f"{LLM_input_key}_input", disabled=True)
            # st.text_input(f"{col} (LLM)", value=suggested_value, key=f"{LLM_input_key}_input", placeholder=suggested_value)

            # Call the function to display the move button
            display_move_button(col, c_move, move_arrow, help_opt='LLM')




def display_helper_input(col, c_help, c_move, move_arrow):
    helper_input_key = f"helper_{col}"

    if st.session_state.tool_access.get('hints'):
        if (col not in st.session_state.prompt_mapping) or (col in st.session_state.hide_fields): # TODO make helper_map a config file
            # Display a disabled text input for alignment purposes
            # st.text_input(f"{col}", '', key=f"disabled_helper_{col}", disabled=True)
            pass
        else:
            helper_key = st.session_state.prompt_mapping[col]
            hint_type = helper_key.split('_')
            suggested_value = str(st.session_state.data[helper_key][st.session_state.row_to_edit])
            if suggested_value:

                # Initialize the session state variable before widget creation
                if helper_input_key not in st.session_state:
                    st.session_state[helper_input_key] = suggested_value
                    
                hint = None
                with c_help:
                    # helper_key = helper_map[col]
                    # suggested_value = str(st.session_state.data[helper_key][st.session_state.row_to_edit])
                    if col == "order":
                        suggested_value = suggested_value.split("|")[3]
                    elif col == "family":
                        suggested_value = suggested_value.split("|")[4]
                    elif col == "scientificName":
                        suggested_value = " ".join([suggested_value.split(" ")[0],suggested_value.split(" ")[1]])
                    elif col == "scientificNameAuthorship":
                        pts = suggested_value.split(" ")[2:]
                        suggested_value = " ".join(pts)
                    elif col == "genus":
                        suggested_value = suggested_value.split("|")[5]
                    elif col == "specificEpithet":
                        suggested_value = suggested_value.split("|")[6]

                    
                    if 'GEO' in hint_type:
                        st.text_input(f"{col} (GEO)", value=suggested_value, key=f"{helper_input_key}_input", placeholder=suggested_value)
                    elif 'WFO' in hint_type:
                        if col == 'specificEpithet':
                            temp_sp = suggested_value.split('$')[0]
                            st.text_input(f"{col} (WFO)", value=temp_sp, key=f"{helper_input_key}_input", placeholder=temp_sp)
                        else:
                            st.text_input(f"{col} (WFO)", value=suggested_value, key=f"{helper_input_key}_input", placeholder=suggested_value)
                    else:
                        st.text_input(f"{col} (hint)", value=suggested_value, key=f"{helper_input_key}_input", placeholder=suggested_value)
                
                display_move_button(col, c_move, move_arrow, help_opt='help')




def get_columns_to_show(group_option):
    #"""Return the columns to be shown based on the group option."""
    # return st.session_state.data_edited.columns if group_option == "ALL" else st.session_state.grouping[group_option]
    exclude_columns = [
        'WFO_override_OCR', 'WFO_exact_match', 'WFO_exact_match_name', 'WFO_best_match', 'WFO_candidate_names',
        'WFO_placement', 'GEO_override_OCR', 'GEO_method', 'GEO_formatted_full_string', 'GEO_decimal_lat',
        'GEO_decimal_long', 'GEO_city', 'GEO_county', 'GEO_state', 'GEO_state_code', 'GEO_country',
        'GEO_country_code', 'GEO_continent', 'current_time', 'inference_time_s', 'tool_time_s', 'max_cpu',
        'max_ram_gb', 'n_gpus', 'max_gpu_load', 'max_gpu_vram_gb', 'total_gpu_vram_gb', 'capability_score',
        'run_name', 'prompt', 'LLM', 'tokens_in', 'tokens_out', 'LM2_collage', 'OCR_method', 'OCR_double', 'OCR_trOCR',
        'path_to_crop', 'path_to_original', 'path_to_content', 'path_to_helper', 'track_view',
        'track_edit', 'track_issues', 'user_uniqname', 'user_time_of_edit', 
    ]
    if group_option == "ALL":
        # Exclude the specified columns if any
        return [col for col in st.session_state.data_edited.columns if col not in exclude_columns]
    else:
        # Return the specific group of columns based on the group_option
        return st.session_state.grouping[group_option]

def prepare_column(col):
    #"""Prepare unique key and color for the given column."""
    unique_key = f"{st.session_state.row_to_edit}_{col}"
    color = find_column_color(col)
    return unique_key, color

def find_column_color(col):
    #"""Find the color for the given column."""
    for group, fields in st.session_state.grouping.items():
        if col in fields:
            return st.session_state.color_map_text.get(group, ":gray")
    return st.session_state.color_map_text.get("MISC", ":red")

def get_color(col):
    #"""Find the color for the given column."""
    for group, fields in st.session_state.grouping.items():
        if col in fields:
            return st.session_state.color_map_text.get(group, ":gray")
    return st.session_state.color_map_text.get("MISC", ":red")

def handle_column_input(col, unique_key, color):
    #"""Handle input for the given column."""
    colored_label = f"{color}[{col}]"
    value = st.session_state.data_edited.loc[st.session_state.row_to_edit, col]
    input_type = determine_input_type(col, value)
    # st.session_state.user_input[col] = input_type(colored_label, value, key=unique_key)
    # update_data_if_changed(col, value)
    # Get user input and replace newline characters with spaces
    if st.session_state.data_edited.loc[st.session_state.row_to_edit, 'country'] == "X":
        is_skipped_specimen = True
    elif col == 'catalogNumber':
        is_skipped_specimen = True
    else:
        is_skipped_specimen = False

    user_input = input_type(colored_label, value, key=unique_key, disabled=is_skipped_specimen)
    if isinstance(user_input, str):  # Ensure the input is a string
        user_input = user_input.replace("\n", " ")
        # Ensure only single spaces, no consecutive spaces
        user_input = " ".join(user_input.split())
    # Store the processed input back into the session state
    st.session_state.user_input[col] = user_input
    
    update_data_if_changed(col, value)

def determine_input_type(col, value):
    #"""Determine the type of input field based on column and conditions."""
    if col == 'catalogNumber':
        return handle_catalog_number_input
    
    if value:
        if len(value) > st.session_state.form_width:
            return st.text_area     
        else:
            return st.text_input
    else:
        return st.text_input

def handle_catalog_number_input(colored_label, value, key, disabled=True):
    #"""Handle input specifically for 'catalogNumber'."""
    access_option = st.session_state.access_option
    if access_option == 'Admin':
        return st.text_input(colored_label, value, key=key)
    elif access_option == 'Labeler':
        return st.text_input(colored_label, value, key=key, disabled=disabled)
    return st.text_input(colored_label, value, key=key)

def update_data_if_changed(col, original_value):
    #"""Update the session state data if the value has changed."""
    if st.session_state.user_input[col] != original_value:
        st.session_state.data_edited.loc[st.session_state.row_to_edit, col] = st.session_state.user_input[col]
        save_data()
        st.rerun()

# def display_helper_data(col):
#     #"""Display helper data for the given column."""
#     helper_key = helper_map[col]
#     suggested_value = getattr(st.session_state, helper_key, None)
#     if suggested_value is not None:
#         st.write(f"Suggested {col}: {suggested_value}")

def display_move_button(col, in_column, move_arrow, help_opt):
    if st.session_state.tool_access.get('arrow'):
        with in_column:
            #"""Display a move button for the given column."""
            # if col in st.session_state.prompt_mapping:
            move_key = f"{col}_to_{col}_edited"
            st.write("")
            st.write("")
            st.button(move_arrow, key=move_key,on_click=move_suggested_data, args=[col, help_opt],use_container_width=True)
            # else:
                # pass


def move_suggested_data(col_to, help_opt):
    """Move suggested data to the main form input for the given column."""
    # helper_value = st.session_state.prompt_mapping[col_to]
    # helper_value_text = st.session_state.data.loc[st.session_state.row_to_edit, helper_value]
    if help_opt == 'help':
        helper_value_text = st.session_state[f"helper_{col_to}_input"]
    else: # 'LLM'
        helper_value_text = st.session_state[f"LLM_{col_to}_input"]

    # if helper_value is not None:
    st.session_state.user_input[col_to] = helper_value_text
    st.session_state.data_edited.at[st.session_state.row_to_edit, col_to] = helper_value_text
    save_data()



def display_lower_case_button(col, in_column):
    if st.session_state.tool_access.get('cap'):
        if col not in st.session_state.hide_fields:
            symbol = ":arrow_double_down:"
            with in_column:
                #"""Display a move button for the given column."""
                # if col in helper_map:
                true_key = f"{col}_lower_"
                st.write("")
                st.write("")
                st.button(symbol, key=true_key,on_click=apply_lower_case, args=[col],use_container_width=True)


def apply_lower_case(col_to):
    if st.session_state.data_edited.at[st.session_state.row_to_edit, col_to] is not None:
        try:
            st.session_state.data_edited.at[st.session_state.row_to_edit, col_to] = st.session_state.data_edited.at[st.session_state.row_to_edit, col_to].lower()
            save_data()
        except Exception as e:
            print(e)
            pass

def display_cap_case_button(col, in_column):
    if st.session_state.tool_access.get('cap'):
        if col not in st.session_state.hide_fields:
            symbol = ":eject:"
            with in_column:
                #"""Display a move button for the given column."""
                # if col in helper_map:
                true_key = f"{col}_cap_"
                st.write("")
                st.write("")
                st.button(symbol, key=true_key,on_click=apply_cap_case, args=[col], use_container_width=True)


def apply_cap_case(col_to):
    if st.session_state.data_edited.at[st.session_state.row_to_edit, col_to] is not None:
        try:
            st.session_state.data_edited.at[st.session_state.row_to_edit, col_to] = st.session_state.data_edited.at[st.session_state.row_to_edit, col_to].capitalize()
            save_data()
        except Exception as e:
            print(e)
            pass

def display_search_button(col, in_column):
    if col not in st.session_state.hide_fields:
        symbol = ":mag:"
        with in_column:
            #"""Display a move button for the given column."""
            # if col in helper_map:
            true_key = f"{col}_search_"
            st.write("")
            st.write("")
            st.button(symbol, key=true_key,on_click=apply_search, args=[col], use_container_width=True)


def apply_search(col_to):
    wrapper = DuckDuckGoSearchAPIWrapper(max_results=2)
    search = DuckDuckGoSearchRun(api_wrapper=wrapper)
    st.session_state.search_results_duckduckgo = None
    
    if st.session_state.data.at[st.session_state.row_to_edit, col_to] is not None:
        try:
            if col_to in st.session_state.search_info_plants:
                query = f"Plant {col_to} " + st.session_state.data.at[st.session_state.row_to_edit, col_to] + "POWO Wikipedia"
            elif col_to in st.session_state.search_info_geo:
                # Handle geography-related queries
                if col_to in ['country', 'stateProvince', 'county', 'municipality']:
                    country = st.session_state.data.at[st.session_state.row_to_edit, 'country']
                    stateProvince = st.session_state.data.at[st.session_state.row_to_edit, 'stateProvince']
                    county = st.session_state.data.at[st.session_state.row_to_edit, 'county']
                    municipality = st.session_state.data.at[st.session_state.row_to_edit, 'municipality']
                    query = ' '.join([municipality, county, stateProvince, country])
                elif col_to in ['decimalLatitude', 'decimalLongitude']:
                    decimalLatitude = st.session_state.data.at[st.session_state.row_to_edit, 'decimalLatitude']
                    decimalLongitude = st.session_state.data.at[st.session_state.row_to_edit, 'decimalLongitude']
                    query = ' '.join([decimalLatitude, decimalLongitude])
                else:
                    query = f"Location {col_to} " + st.session_state.data.at[st.session_state.row_to_edit, col_to]
            elif col_to in st.session_state.search_info_people:
                query = f"Botanist Person {col_to} " + st.session_state.data.at[st.session_state.row_to_edit, col_to]
            else:
                query = st.session_state.data.at[st.session_state.row_to_edit, col_to]
                
            # Run the search
            res = search.run(query).replace('...', '\n\n')
            
            # Create a search URL for DuckDuckGo
            search_url = f"https://duckduckgo.com/?q={query.replace(' ', '+')}"
            
            # Direct link using markdown with target="_blank" to open in a new tab
            st.markdown(f'<a href="{search_url}" target="_blank">**Open DuckDuckGo Search for {query}**</a>', unsafe_allow_html=True)

            st.session_state.search_term = query
            
            # If Google search option is enabled
            if st.session_state.google_search_new_window:
                google_search_url = f"https://www.google.com/search?q={st.session_state.search_term.replace(' ', '+')}"
                # Direct link using markdown for Google search
                st.markdown(f'<a href="{google_search_url}" target="_blank">**Search Google for {st.session_state.search_term}**</a>', unsafe_allow_html=True)

        except Exception as e:
            st.error(f"An error occurred: {e}")
            pass




def load_yaml_to_json(fullpath):
    try:
        with open(fullpath, 'r') as yaml_file:
            json_data = yaml.safe_load(yaml_file)
            # Convert the YAML data to JSON format
            json_data_str = json.dumps(json_data, indent=4)

            return json_data_str
    except Exception as e:
        print(f"Error loading YAML file: {e}")
        return None
###############################################################
################# Display JSON Helper Text ####################
###############################################################
def display_WFO_partial_match():
    if st.session_state.tool_access.get('wfo_links'):
        if st.session_state.wfo_match_level == "Partial Match":
            with st.expander(f"{get_color('scientificName')}[**WFO** Suggested Taxonomy]"):
                partial_matches = st.session_state.data_edited['WFO_candidate_names'][st.session_state.row_to_edit].split('|')
                temp = []
                ii = 0
                for partial_match in partial_matches:
                    if partial_match not in temp:
                        ii += 1
                        temp.append(partial_match)
                        partial_match_url, partial_match_url_search = get_wfo_url(partial_match)
                        if partial_match_url:
                            st.link_button(label=partial_match,url=partial_match_url)
                        # st.write(f"{ii}) {partial_match}")

@st.cache_data
def display_prompt_template():
    prompt_json = load_yaml_to_json(st.session_state.fullpath_prompt)
    if st.session_state.fullpath_prompt and st.session_state.fullpath_prompt:
        with st.expander(f"Transcription Prompt :arrow_forward: {st.session_state.prompt_name}"):
            st.json(prompt_json)



def display_conversion_calculator():
    with st.expander("Conversion Calculator", expanded=True):
        c_calc_1, c_calc_2 = st.columns(2)
        
        # Initialize session state values if they don't exist
        if 'feet' not in st.session_state:
            st.session_state.feet = '0'
        if 'meters' not in st.session_state:
            st.session_state.meters = '0'

        # Conversion factors
        feet_to_meters_factor = 0.3048
        meters_to_feet_factor = 1 / feet_to_meters_factor

        # Function to update meters when feet changes
        def update_meters():
            try:
                feet_value = float(st.session_state.feet)
                st.session_state.meters = str(int(round(feet_value * feet_to_meters_factor, 0)))
            except ValueError:
                st.session_state.meters = "Invalid input"

        # Function to update feet when meters changes
        def update_feet():
            try:
                meters_value = float(st.session_state.meters)
                st.session_state.feet = str(int(round(meters_value * meters_to_feet_factor, 0)))
            except ValueError:
                st.session_state.feet = "Invalid input"

        # Input fields for feet and meters with callback functions
        with c_calc_1:
            st.text_input("Feet", key="feet", on_change=update_meters)
        with c_calc_2:
            st.text_input("Meters", key="meters", on_change=update_feet)


def display_json_helper_text():
    # Check for the presence of 'OCR_JSON' in session state
    if 'OCR_JSON' in st.session_state:
        OCR_JSON = st.session_state['OCR_JSON']
        
        # Button to toggle extra helper text
        with st.expander("OCR Text"):
            tabs = []
            tab_labels = []

            # Create dynamic tabs based on the keys in OCR_JSON
            available_keys = list(OCR_JSON.keys())
            tab_labels.extend([key.replace('_', ' ').capitalize() for key in available_keys])

            # Clean the text using remove_number_lines and prepare for display
            for key in available_keys:
                cleaned_text = remove_number_lines(OCR_JSON[key], threshold=6)
                tabs.append(cleaned_text.replace('\n', '<br/>'))

            # Check if we have content for all tabs
            if len(tab_labels) != len(tabs):
                st.error("Mismatch between tabs and content")
                return

            # Create the tabs in Streamlit
            tab_instances = st.tabs(tab_labels)

            # Display the cleaned content in each tab
            for i in range(len(tab_instances)):
                with tab_instances[i]:
                    st.markdown(f"""<p style='font-size:16px;'>{tabs[i]}</p><br>""", unsafe_allow_html=True)



def display_issues():
    active_issues = st.session_state.data_edited["track_issues"].eq('True').any()

    with st.expander(":red[Open ISSUES]", expanded=active_issues):
        if active_issues:
            active_issues_indices = st.session_state.data_edited.index[st.session_state.data_edited["track_issues"].eq('True')].tolist()

            for issue in active_issues_indices:
                genus_value  = st.session_state.data_edited.loc[issue, "genus"]
                specificEpithet_value  = st.session_state.data_edited.loc[issue, "specificEpithet"]
                str_genus = str(genus_value) if genus_value is not None else ""
                str_specificEpithet = str(specificEpithet_value) if specificEpithet_value is not None else ""

                if st.button(f"Img [{issue+1}] {str_genus} {str_specificEpithet}"):
                    st.session_state.row_to_edit = int(issue)
                    st.rerun()

def display_notes():
    with st.expander("Notes", expanded=True):
        new_notes = st.text_area("session notes", 
                                 label_visibility='collapsed', 
                                 value=st.session_state.notes_data['NOTES'], 
                                 height=238)
        if new_notes != st.session_state.notes_data['NOTES']:
            st.session_state.notes_data['NOTES'] = new_notes
            save_notes(st.session_state.notes_data['NOTES'])


def display_tab_content(tab, main_key, main_value):
    """
    Display content for a specific tab.
    """
    with tab:
        color = st.session_state.color_map_json.get(main_key, "black")  # Default to black if key is not in color_map
        st.markdown(f"<h4 style='color: {color};'>{main_key}</h4><br>", unsafe_allow_html=True)
        
        if isinstance(main_value, dict):
            for sub_key, sub_value in main_value.items():
                if sub_value:
                    sub_value_show = remove_number_lines(sub_value)
                    sub_value_show = sub_value_show.replace('\n', '<br/>')
                    st.markdown(f"<b style='font-size:20px;'>{sub_key}: <br></b> {sub_value_show}<br>", unsafe_allow_html=True)

def on_press_show_helper_text():
    if st.button('Predicted Text',key=f"Show_help2", use_container_width=True, type="secondary"):
        if st.session_state.show_helper_text == True:
            st.session_state.show_helper_text = False
        elif st.session_state.show_helper_text == False:
            st.session_state.show_helper_text = True

def display_wiki_taxa_main_links():
    if not st.session_state.tool_access.get('taxa_links'):
        return  # Exit if taxa_links tool access is not granted
    
    try:
        if st.session_state.tool_access.get('taxa_links'):
            fname = st.session_state.data_edited['filename'][st.session_state.row_to_edit]

            if fname not in st.session_state.wiki_file_dict:
                return  # Exit gracefully if fname key doesn't exist
            
            wiki_json_path = st.session_state.wiki_file_dict[fname]

            if wiki_json_path:
                try:
                    with open(wiki_json_path, "r") as file:
                        wiki_json = json.load(file)
                except (FileNotFoundError, json.JSONDecodeError, IOError):
                    # Handle file not found, invalid JSON, or other IO errors
                    return

                wiki_taxa = wiki_json.get('WIKI_TAXA', None)
                wiki_taxa_data = wiki_taxa.get('DATA', None)
                wiki_taxa_page_title = wiki_taxa.get('PAGE_TITLE', None)
                wiki_taxa_page_link = wiki_taxa.get('PAGE_LINK', None)

                c_help_left, c_help_right = st.columns([1,1])

                with c_help_left:
                    if wiki_taxa_page_title and wiki_taxa_page_link:
                        st.link_button(label=f":violet[:information_source: {wiki_taxa_page_title}]",url=wiki_taxa_page_link)

                with c_help_right:
                    if wiki_taxa_data:
                        if 'GRIN' in wiki_taxa_data:
                            if wiki_taxa_data.get('GRIN',None):
                                st.link_button(label=f"{get_color('scientificName')}[GRIN]",url=wiki_taxa_data.get('GRIN', None))
                c_help_left, c_help_right = st.columns([1,1])

                with c_help_left:
                    if wiki_taxa_data:
                        if 'POWOID' in wiki_taxa_data:
                            if wiki_taxa_data.get('POWOID',None):
                                st.link_button(label=f"{get_color('scientificName')}[POWO]",url=wiki_taxa_data.get('POWOID', None))

                # with c_help_right:
                #     if wiki_taxa_data:
                #         if 'POWOID_syn' in wiki_taxa_data:
                #             if wiki_taxa_data.get('POWOID_syn',None):
                #                 st.link_button(label=f"{get_color('scientificName')}[POWO Syn.]",url=wiki_taxa_data.get('POWOID_syn', None))
    except Exception as e:
        print(e)
        

@st.cache_data
def display_wiki_taxa_sub_links():
    try:
        fname = st.session_state.data_edited['filename'][st.session_state.row_to_edit]

        if fname not in st.session_state.wiki_file_dict:
            return
        
        wiki_json_path = st.session_state.wiki_file_dict[fname]

        if wiki_json_path:
            with open(wiki_json_path, "r") as file:
                wiki_json = json.load(file)

            wiki_taxa = wiki_json.get('WIKI_TAXA', None)
            wiki_taxa_links = wiki_taxa.get('LINKS', None)
            
            if wiki_taxa_links:
                with st.expander('Top Wikipedia Links'):
                    for label, link in wiki_taxa_links.items():
                        st.link_button(label=label,url=link)
    except Exception as e:
        print(e)
        


@st.cache_data
def display_wiki_taxa_summary():
    try:
        fname = st.session_state.data_edited['filename'][st.session_state.row_to_edit]

        if fname not in st.session_state.wiki_file_dict:
            return
        
        wiki_json_path = st.session_state.wiki_file_dict[fname]

        if wiki_json_path:
            with open(wiki_json_path, "r") as file:
                wiki_json = json.load(file)

            wiki_taxa = wiki_json.get('WIKI_TAXA', None)
            wiki_taxa_summary = wiki_taxa.get('SUMMARY', None)

            if wiki_taxa_summary:
                with st.expander(f"{get_color('scientificName')}[Wikipedia Summary - Taxonomy]"):
                    st.write(wiki_taxa_summary.strip())
    except Exception as e:
        print(e)
        

@st.cache_data
def display_wiki_geo_main_links():
    try:
        fname = st.session_state.data_edited['filename'][st.session_state.row_to_edit]

        if fname not in st.session_state.wiki_file_dict:
            return
        
        wiki_json_path = st.session_state.wiki_file_dict[fname]

        if wiki_json_path:
            with open(wiki_json_path, "r") as file:
                wiki_json = json.load(file)
            wiki_geo = wiki_json.get('WIKI_GEO', None)
            wiki_geo_links = wiki_geo.get('LINKS', None)
            wiki_geo_data = wiki_geo.get('DATA', None)
            wiki_geo_summary = wiki_geo.get('SUMMARY', None)
            wiki_geo_page_link = wiki_geo.get('PAGE_LINK', None)
            wiki_geo_page_title = wiki_geo.get('PAGE_TITLE', None)

            wiki_locality = wiki_json.get('WIKI_LOCALITY', None)
            wiki_locality_data = wiki_locality.get('DATA', None)
            wiki_locality_summary = wiki_locality.get('SUMMARY', None)
            wiki_locality_page_link = wiki_locality.get('PAGE_LINK', None)
            wiki_locality_page_title = wiki_locality.get('PAGE_TITLE', None)

            c_help_left, c_help_right = st.columns([1,1])

            with c_help_left:
                if wiki_geo_page_title and wiki_geo_page_link:
                    st.link_button(label=f"{get_color('country')}[:information_source: {wiki_geo_page_title}]",url=wiki_geo_page_link)

            with c_help_right:
                if wiki_locality_page_title and wiki_locality_page_link:
                    st.link_button(label=f"{get_color('country')}[:information_source: {wiki_locality_page_title}]",url=wiki_locality_page_link)
    except Exception as e:
        print(e)


def display_search_results():
    with st.expander(":mag: :rainbow[Search Results]"):
        if st.session_state.search_results_duckduckgo:
            st.write(f"{st.session_state.search_results_duckduckgo}")
        else:
            st.empty()


def display_google_search():
    loc = st.session_state.location_google_search
    search_url = f"https://www.google.com/search?igu=1&ei=&q={st.session_state.search_term}"

    if loc == 'Top':
        with st.expander(":rainbow[Google Search]"):#,key=f"Google Search{loc}"):
            st.markdown(":green[**Right-click links to open in new tab. Required for most websites (other than Wikipedia)**]")
            # search = st.text_input("What do you want to search for?")
            components.iframe(search_url, height=500,scrolling=True)
    elif loc == 'Hint Panel':
        with st.expander(":rainbow[Google Search]"):#,key=f"Google Search{loc}"):
            # search = st.text_input("What do you want to search for?")
            components.iframe(search_url, height=500,scrolling=True)
    elif loc == 'Bottom':
        with st.expander(":rainbow[Google Search]"):#,key=f"Google Search{loc}"):
            # search = st.text_input("What do you want to search for?")
            components.iframe(search_url, height=1000,scrolling=True)

        

###############################################################
###################### Validate Fields ########################
###############################################################
def display_coordinates(n):
    with st.expander(f":earth_africa: {get_color('country')}[Mapped Coordinates]", expanded=True):
        verbatim_coordinates = st.session_state.data_edited.loc[st.session_state.row_to_edit, 'verbatimCoordinates']

        decimal_lat = st.session_state.data_edited.loc[st.session_state.row_to_edit, 'decimalLatitude']
        decimal_long = st.session_state.data_edited.loc[st.session_state.row_to_edit, 'decimalLongitude']
        decimal_coordinates = ','.join([decimal_lat,decimal_long])

        # decimal_lat_geo = st.session_state.data_edited.loc[st.session_state.row_to_edit, 'GEO_decimal_lat']
        # decimal_long_geo = st.session_state.data_edited.loc[st.session_state.row_to_edit, 'GEO_decimal_long']
        # decimal_coordinates_geo = ','.join([decimal_lat_geo,decimal_long_geo])

        # annotated_text(("Verbatim Coordinates", "", "#b86602"), ("Decimal Coordinates", " ", "#017d16"), ("Geolocation Hint", " ", "#0232b8"))
        annotated_text(("Verbatim Coordinates", "", "#0232b8"), ("Decimal Coordinates", " ", "#017d16"))

        if verbatim_coordinates:
            verbatim_map_data = validate_and_get_coordinates(verbatim_coordinates, 'verbatim')
        else:
            verbatim_map_data = None
        
        if decimal_coordinates:
            decimal_map_data = validate_and_get_coordinates(decimal_coordinates, 'decimal')
        else:
            decimal_map_data = None

        # if decimal_coordinates:
        #     decimal_geo_map_data = validate_and_get_coordinates(decimal_coordinates_geo, 'Geolocation Hint')
        # else:
        #     decimal_geo_map_data = None

        # Prepare a list for DataFrames that are not None
        map_data_frames = []

        if verbatim_map_data is not None:
            map_data_frames.append(verbatim_map_data)

        if decimal_map_data is not None:
            map_data_frames.append(decimal_map_data)

        # if decimal_geo_map_data is not None:
        #     map_data_frames.append(decimal_geo_map_data)

        # Only proceed if there's at least one valid DataFrame
        if map_data_frames:
            if len(map_data_frames) > 1:
                # Check if we need to zoom out
                zoom_out = should_zoom_out(map_data_frames[0]['lat'][0], map_data_frames[0]['lon'][0],
                                        map_data_frames[1]['lat'][0], map_data_frames[1]['lon'][0])
            else:
                zoom_out = False  # Or some default behavior if there's only one set of coordinates

            # Concatenate all valid DataFrames and reset the index
            combined_map_data = pd.concat(map_data_frames).reset_index(drop=True)
            display_map(combined_map_data, zoom_out, n)
        else:
            # Handle the case where all map data is None, if needed
            st.write("No valid coordinates to display.")


        # if verbatim_map_data is not None and decimal_map_data is not None:
        #     zoom_out = should_zoom_out(verbatim_map_data['lat'][0], verbatim_map_data['lon'][0], decimal_map_data['lat'][0], decimal_map_data['lon'][0])
        #     combined_map_data = pd.concat([verbatim_map_data, decimal_map_data, decimal_geo_map_data]).reset_index(drop=True)
        #     display_map(combined_map_data, zoom_out)
        # # else:
        #     zoom_out = False
        #     st.session_state.coordinates_dist = None
        #     display_map(verbatim_map_data, zoom_out)
        #     display_map(decimal_map_data, zoom_out)
        #     display_map(decimal_geo_map_data, zoom_out)

def get_map_data(coords_string, coordinate_type):
    # coords = re.split(',|-\s', coords_string.strip())
    coords = re.split(r',|-\s', coords_string.strip())
    if len(coords) != 2:
        st.warning(f"Possibly invalid {coordinate_type} GPS coordinates! Exactly two coordinate values not found.")
        return None
    lat, lon = parse_coordinate(coords)
    if lat is not None and lon is not None:
        if not ((-90 <= lat <= 90) or (-180 <= lon <= 180)):
            st.warning(f"Invalid {coordinate_type} GPS coordinates! Values are out of bounds.")
            return None
    if lat is None or lon is None:
        st.info(f"No GPS coordinates in record")
        return None
    if coordinate_type == 'decimal':
        color = [[0.0, 1.0, 0.0, 0.5]]  # Decimal for green
        if st.session_state.pinpoint == "Pinpoint":
            size = [100]  # Decimal for green
        else:
            size = [100000]  # Decimal for green
    elif coordinate_type == 'Geolocation Hint':
        color = [[0.2, 0.5, 1.0, 0.5]]  # Decimal for blue
        if st.session_state.pinpoint == "Pinpoint":
            size = [150]  # Decimal for green
        else:
            size = [150000]  # Decimal for green
    elif coordinate_type == 'verbatim':
        # color = [[1.0, 0.5, 0.0, 0.5]]# Decimal for orange
        color = [[0.2, 0.5, 1.0, 0.5]]  # Decimal for blue
        if st.session_state.pinpoint == "Pinpoint":
            size = [150]  
        else:
            size = [150000] 
    else:
        color = [[1.0, 0.0, 0.0, 0.5]]  # Decimal for red
        if st.session_state.pinpoint == "Pinpoint":
            size = [250]  
        else:
            size = [250000]  
    # print({'lat': [lat], 'lon': [lon], 'color': color})
    return pd.DataFrame({'lat': [lat], 'lon': [lon], 'color': color, 'size':size})



def display_map(map_data, zoom_out, n):
    if map_data is not None and not map_data.empty:
        if zoom_out:
            z = 0
            st.map(map_data, zoom=z, color='color', height=st.session_state.set_map_height_pxh, size='size')
            if st.session_state.coordinates_dist:
                st.error(f':heavy_exclamation_mark: The verbatim and decimal coordinates are {st.session_state.coordinates_dist} kilometers apart. Check the coordinates:heavy_exclamation_mark:')
        else:
            z = 3
            st.map(map_data, zoom=z, color='color', height=st.session_state.set_map_height_pxh, size='size')
            if st.session_state.coordinates_dist:
                if st.session_state.coordinates_dist > st.session_state.distance_GPS_warn:
                    st.warning(f':bell: ***WARNING:*** Distance between verbatim and decimal coordinates is ***{st.session_state.coordinates_dist}*** kilometers. Check the coordinates!')
                
                else:
                    st.info(f'The verbatim and decimal coordinates are ***{st.session_state.coordinates_dist}*** kilometers apart :earth_africa:')
            elif st.session_state.coordinates_dist == 0.0:
                st.info(f':white_check_mark: Verbatim and Decimal coordinates are the same')

        current_map_size = st.session_state.pinpoint
        st.session_state.pinpoint = st.radio('Map Dot Size', options=["Broad", "Pinpoint"], index=0, key=f'Map Dot Size{n}')
        if current_map_size != st.session_state.pinpoint:
            st.rerun()


def validate_and_get_coordinates(coordinate_str, coordinate_type):
    try:
        do_warn = check_for_sep(coordinate_str)
        if do_warn:
            st.warning(f"Possibly invalid {coordinate_type} GPS coordinates! Lacks separator , - | ")
        map_data = get_map_data(coordinate_str, coordinate_type)
        return map_data
    except Exception as e:
        st.error(f"{e} Invalid {coordinate_type} GPS coordinates!\nIncorrect OR unsupported coordinate format.")
        return None
    

def haversine_distance(lat1, lon1, lat2, lon2):
    # Convert degrees to radians
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    
    # Haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    r = 6371 # Radius of Earth in kilometers
    return r * c


def should_zoom_out(lat1, lon1, lat2, lon2):
    st.session_state.coordinates_dist = 0
    st.session_state.coordinates_dist = round(haversine_distance(lat1, lon1, lat2, lon2),2)
    return st.session_state.coordinates_dist > st.session_state.zoom_dist  # Return True if distance is more than 45 km
###############################################################
###################### Image Handling #########################
###############################################################
def safe_open_image(image_path, fallback_path=os.path.join(WORKING_DIR, 'img', 'icon.jpg')):
    try:
        return Image.open(image_path), image_path
    except Exception as e:
        print(e)
        print(f"Using fallback image {fallback_path}")
        # Handle various possible errors when opening an image
        return Image.open(fallback_path), fallback_path

def image_path_and_load():
    # Check if the current row or image option has changed
    if ((st.session_state['last_row_to_edit'] != st.session_state.row_to_edit) or 
        ('last_image_option' not in st.session_state) or 
        (st.session_state['last_image_option'] != st.session_state.image_option) or 
        st.session_state.image_rotation_change):

        print("ROUTING")
        print(f"    new row                --- {st.session_state['last_row_to_edit'] != st.session_state.row_to_edit} --- row {st.session_state.row_to_edit}")
        print(f"    image_option not in st --- {'last_image_option' not in st.session_state}")
        print(f"    image_option changed   --- {st.session_state['last_image_option'] != st.session_state.image_option} --- {st.session_state.image_option}")
        print(f"    image was rotated      --- {st.session_state.image_rotation_change} --- {st.session_state.image_rotation}")

        # Remember the selected image option
        st.session_state['last_image_option'] = st.session_state.image_option
        st.session_state.last_row_to_edit = st.session_state.row_to_edit

        # Update the image path based on the selected image option
        if st.session_state.image_option == 'Original':
            # st.session_state['image_path'] = st.session_state.data_edited.loc[st.session_state.row_to_edit, "path_to_original"]
            # st.session_state['image'] = Image.open(st.session_state['image_path'])
            st.session_state['image'], st.session_state['image_path'] = safe_open_image(st.session_state.data_edited.loc[st.session_state.row_to_edit, "path_to_original"])
            st.session_state.relative_path_to_static = image_to_server()
        elif st.session_state.image_option == 'Cropped':
            # st.session_state['image_path'] = st.session_state.data_edited.loc[st.session_state.row_to_edit, "path_to_crop"]
            # st.session_state['image'] = Image.open(st.session_state['image_path'])
            st.session_state['image'], st.session_state['image_path'] = safe_open_image(st.session_state.data_edited.loc[st.session_state.row_to_edit, "path_to_crop"])
            st.session_state.relative_path_to_static = image_to_server()
        elif st.session_state.image_option == 'Helper':
            # st.session_state['image_path'] = st.session_state.data_edited.loc[st.session_state.row_to_edit, "path_to_helper"]
            # st.session_state['image'] = Image.open(st.session_state['image_path'])
            st.session_state['image'], st.session_state['image_path'] = safe_open_image(st.session_state.data_edited.loc[st.session_state.row_to_edit, "path_to_helper"])
            st.session_state.relative_path_to_static = image_to_server()

        # Load the image if the image path is not null
        if st.session_state.image_rotation_change:
            if pd.notnull(st.session_state['image_path']):
                new_img_path = st.session_state['image_path']
                new_img_path_fname = os.path.basename(new_img_path)
                print(f'LOADING IMAGE: {new_img_path_fname}')
                # st.session_state['image_path'] = new_img_path
                # st.session_state['image'] = apply_image_rotation(Image.open(new_img_path))
                st.session_state['image'] = apply_image_rotation(new_img_path)
            st.session_state.image_rotation_change = False
            st.session_state.relative_path_to_static = image_to_server()
        
        
def apply_image_rotation(image):
    if st.session_state.image_rotation == 'left':
        return image.rotate(90, expand=True)
    elif st.session_state.image_rotation == 'right':
        return image.rotate(-90, expand=True)
    elif st.session_state.image_rotation == '180':
        return image.rotate(180, expand=True)
    else:
        return image
    
def image_to_server():

    # image_path = st.session_state['image_path']
    # print(image_path)
    if 'image_rotation' in st.session_state and st.session_state.image_rotation in ['left', 'right', '180']:

        # Save the rotated image to a temporary file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(st.session_state['image_path'])[1])
        st.session_state['image'].save(temp_file.name)
        image_path = temp_file.name  # Update image_path to point to the rotated image
        st.session_state['image_path'] = image_path
        # st.session_state.image_rotation_change = False
    
    # Continue with the existing logic to determine the destination path
    if st.session_state.image_option == 'Original':
        static_image_path = os.path.join('static_og', os.path.basename(st.session_state['image_path']))
        shutil.copy(st.session_state['image_path'], os.path.join(st.session_state.static_folder_path_o, os.path.basename(st.session_state['image_path'])))
    elif st.session_state.image_option == 'Cropped':
        static_image_path = os.path.join('static_cr', os.path.basename(st.session_state['image_path']))
        shutil.copy(st.session_state['image_path'], os.path.join(st.session_state.static_folder_path_c, os.path.basename(st.session_state['image_path'])))
    elif st.session_state.image_option == 'Helper':
        static_image_path = os.path.join('static_h', os.path.basename(st.session_state['image_path']))
        shutil.copy(st.session_state['image_path'], os.path.join(st.session_state.static_folder_path_h, os.path.basename(st.session_state['image_path'])))
    
    # Generate and print the relative path to the static directory
    relative_path_to_static = os.path.relpath(static_image_path, st.session_state.current_dir).replace('\\', '/')
    print(f"Adding to Zoom image server: {relative_path_to_static}")
    return relative_path_to_static


def display_image_options_buttons(relative_path_to_static, zoom_1, zoom_2, zoom_3, zoom_4):
    """
    Display buttons for different image options.
    The number and type of buttons displayed depends on st.session_state.use_extra_image_options.
    """
    # Define the Zoom link
    link = f'http://localhost:{st.session_state.http_server_port}/{relative_path_to_static}'
    
    current_image = st.session_state.image_option
    if st.session_state.use_extra_image_options:
        with zoom_1:
            if st.button('Original', use_container_width=True):
                st.session_state.image_option = 'Original'
        with zoom_2:
            if st.button('Zoom', use_container_width=True):
                webbrowser.open_new_tab(link)
        with zoom_3:
            if st.button('Toggle Fitted', use_container_width=True):
                st.session_state.is_fitted_image = not st.session_state.is_fitted_image
                st.session_state.set_image_size = 'Fitted' if st.session_state.is_fitted_image else st.session_state.set_image_size_previous
        if st.session_state.tool_access.get('ocr'):
            with zoom_4:
                if st.button('Collage', use_container_width=True):
                    st.session_state.image_option = 'Cropped'
    else:
        with zoom_1:
            if st.button('Original', use_container_width=True, help="View the full specimen image"):
                st.session_state.image_option = 'Original'
        with zoom_2:
            if st.button('Zoom', use_container_width=True, help="Open the current image in a new tab. Can zoom in."):
                webbrowser.open_new_tab(link)
        with zoom_3:
            if st.button('Collage', use_container_width=True, help="View the LeafMachine2 label collage. Shows all text ONLY."):
                st.session_state.image_option = 'Cropped'
        if st.session_state.tool_access.get('ocr'):
            with zoom_4:
                if st.button('OCR', use_container_width=True):
                    st.session_state.image_option = 'Helper'
    last_image_option = st.session_state.image_option
    if current_image != last_image_option:
        st.rerun()


def display_image_rotation_buttons(r1, r2, r3, r4):
    st.session_state.image_rotation_previous
    with r1:
        if st.button(':arrow_right_hook:', use_container_width=True,help="Rotate image 90 degrees counterclockwise"):
            st.session_state.image_rotation = 'left'
            if st.session_state.image_rotation_previous != st.session_state.image_rotation:
                st.session_state.image_rotation_previous = st.session_state.image_rotation
                st.session_state.image_rotation_change = True
                st.rerun()

    with r2:
        if st.button(':leftwards_arrow_with_hook:', use_container_width=True,help="Rotate image 90 degrees clockwise"):
            st.session_state.image_rotation = 'right'
            if st.session_state.image_rotation_previous != st.session_state.image_rotation:
                st.session_state.image_rotation_previous = st.session_state.image_rotation
                st.session_state.image_rotation_change = True
                st.rerun()
    with r3:
        if st.button(':arrow_double_down:', use_container_width=True,help="Rotate image 180 degrees"):
            st.session_state.image_rotation = '180'
            if st.session_state.image_rotation_previous != st.session_state.image_rotation:
                st.session_state.image_rotation_previous = st.session_state.image_rotation
                st.session_state.image_rotation_change = True
                st.rerun()
    with r4:
        if st.button(':arrow_double_up:', use_container_width=True,help="Normal"):
            st.session_state.image_rotation = '0'
            if st.session_state.image_rotation_previous != st.session_state.image_rotation:
                st.session_state.image_rotation_previous = st.session_state.image_rotation
                st.session_state.image_rotation_change = True
                st.rerun()


def display_scrollable_image(con_image):
    """
    Display the image from st.session_state in a scrollable container.
    The width and height of the container are determined by st.session_state values.
    """
    # Initialize the container
    with con_image:
        display_scrollable_image_method()


def display_scrollable_image_method():

    # Determine the desired width based on st.session_state.set_image_size
    if st.session_state.set_image_size == "Auto Width":
        st.image(st.session_state['image'], caption=st.session_state['image_path'], use_container_width=True)
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
        image_width = st.session_state.set_image_size_px  # For use_container_width=True

    # Convert the image to base64
    if isinstance(st.session_state['image'], str):
        st.session_state['image'], st.session_state['image_path'] = safe_open_image(st.session_state['image'])

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
            text-align: left;
            margin-left: 0;
        }}
    </style>
    """
    css_img_left = f"""
    <style>
        .scrollable-image-container {{
            overflow: auto;
            height: {st.session_state.set_image_size_pxh}vh;
            width: 70vw;
            direction: rtl;
            text-align: left;
            margin-left: 0;
        }}
    </style>
    """

    is_img_left = False
    pts = st.session_state.image_fill.split(" ")
    if "Left" in pts:
        is_img_left = True

    if is_img_left:
        st.markdown(css_img_left, unsafe_allow_html=True)
    else:
        # Apply the CSS and then the image
        st.markdown(css, unsafe_allow_html=True)
    st.markdown(img_html, unsafe_allow_html=True)



def display_help():
    st.write('---')
    st.subheader("Help")
    with st.expander(":grey_question: Image Buttons"):
        st.write("**Buttons**")
        st.write(HelpText.help_btns)
    with st.expander(":grey_question: Tool Hints"):
        st.write("**Buttons**")
        st.write(HelpText.help_form_btns)
        st.write("**Tool Hints**")
        st.write(HelpText.help_form)
    with st.expander(":grey_question: Specimen Record"):
        st.write("**Specimen Record**")
        st.write(HelpText.help_specimen)
    with st.expander(":grey_question: Enabling/Hiding Tools"):
        st.write("**Enabling/Hiding Tools**")
        st.write(HelpText.help_hide_tools)
    with st.expander(":grey_question: Categories"):
        st.write("**Categories**")
        st.write(HelpText.help_categories)
    with st.expander(":grey_question: Other"):
        st.write("**World Flora Online Badge**")
        st.write(HelpText.help_WFO_badge)
        st.write("**Categories**")
        st.write(HelpText.help_WFO_badge)




def load_yaml_settings(file_path):
    """Load YAML settings from a file."""
    try:
        if platform.system() == 'Darwin':
            file_path = f'/{file_path}'
        with open(file_path, 'r') as file:
            return yaml.safe_load(file)
    except Exception as e:
        st.error(f"Failed to load settings: {e}")
        return None

def save_yaml_settings(file_path, data):
    """Save YAML settings to a file."""
    try:
        if platform.system() == 'Darwin':
            file_path = f'/{file_path}'
        with open(file_path, 'w') as file:
            yaml.dump(data, file)
        st.success("Settings saved successfully.")
    except Exception as e:
        st.error(f"Failed to save settings: {e}")

def dynamic_fields_section(section_name, data):
    """Generate dynamic input fields for a section and handle changes."""
    temp_data = data.copy()  # Create a copy of the data to work with
    for key, value in temp_data.items():
        if key == "mapping":
            for key2, value2 in temp_data.items():
                user_input = st.text_input(f"{key2} (comma-separated)", value=value2, key=f"{section_name}_{key2}_{value2}")
                temp_data['mapping'][key2] = value2

    if section_name == 'mapping':
        # Apply collected changes to the original data
        for key, value in temp_data.items():
            data['mapping'][key] = value
    return data

        
def edit_default_settings_yaml():
    file_path = os.path.join(st.session_state.dir_home, 'settings', 'default.yaml')
    
    # Start a form for user inputs
    with st.form("edit_settings"):
        st.write("NOTE: Spaces, dashes, and special symbols in keys and values is not allowed.")
        hide_fields = st.text_input("Hide Fields (comma-separated)", value=",".join(st.session_state.settings['editor']['hide_fields']))
        
        f1, f2 = st.columns([1,2])
        # Use session state to keep track of dynamic add_field keys
        if 'add_fields_count' not in st.session_state:
            st.session_state.add_fields_count = len(st.session_state.settings['editor']['add_fields'])

        # Generate inputs for existing add_fields
        for key, value in list(st.session_state.settings['editor']['add_fields'].items()):
            user_input = st.text_input(f"{key} (added category)", value=",".join(value), key=key)
            st.session_state.settings['editor']['add_fields'][key] = [field.strip() for field in user_input.split(",") if field.strip()]

        
        # # Dynamic fields for add_fields
        # dynamic_fields_section("Add Fields", settings['editor'].get('add_fields', {}))

        # if st.session_state.data is None:
        #     st.write("#### Select a transcription.xlsx file to see the full current configuration")
        # else:
        #     # Dynamic fields for mapping
        #     dynamic_fields_section("Mapping", st.session_state.prompt_json)

        # Placeholder for new field inputs
        for i in range(st.session_state.add_fields_count - len(st.session_state.settings['editor']['add_fields'])):
            with f1:
                new_key = st.text_input("New Field Key (single new or existing category)", key=f"new_key_{i}")
            with f2:
                new_value = st.text_input("New Field Values (comma-separated list)", key=f"new_value_{i}")
            if new_key and new_value:
                st.session_state.settings['editor']['add_fields'][new_key] = [field.strip() for field in new_value.split(",") if field.strip()]

        # Form submission
        submitted = st.form_submit_button("Save")
        if submitted:
            # Update settings based on user inputs
            st.session_state.settings['editor']['hide_fields'] = [field.strip() for field in hide_fields.split(",") if field.strip()]

            # Save updated settings back to YAML
            save_yaml_settings(file_path, st.session_state.settings)

    # Button to add more fields
    if st.button("Add new fields"):
        st.session_state.add_fields_count += 1
        # st.rerun()


def edit_mapping():
    st.header("Edit Mapping")
    st.write("Assign each column name to a single category.")
    st.session_state['refresh_mapping'] = False

    # Dynamically create a list of all column names that can be assigned
    # This assumes that the column names are the keys in the dictionary under 'rules'
    if st.session_state.prompt_json:
        all_column_names = list(st.session_state.prompt_json['mapping'].keys())

        categories = ['TAXONOMY', 'GEOGRAPHY', 'LOCALITY', 'COLLECTING', 'MISC']

        if ('mapping' not in st.session_state) or (st.session_state['mapping'] == {}):
            st.session_state['mapping'] = {category: [] for category in categories}

        if 'assigned_columns' not in st.session_state:
            st.session_state['assigned_columns'] = []
            for category in categories:
                list_of_maps = st.session_state.prompt_json['mapping'][category]
                for m in list_of_maps:
                    st.session_state['assigned_columns'].append(m)

        for category in categories:
            # Filter out the already assigned columns
            available_columns = [col for col in all_column_names if col not in st.session_state['assigned_columns'] or col in st.session_state['mapping'].get(category, [])]

            # Ensure the current mapping is a subset of the available options
            current_mapping = [col for col in st.session_state['mapping'].get(category, []) if col in available_columns]

            # Provide a safe default if the current mapping is empty or contains invalid options
            safe_default = current_mapping if all(col in available_columns for col in current_mapping) else []

            # Create a multi-select widget for the category with a safe default
            selected_columns = st.multiselect(
                f"Select columns for {category}:",
                available_columns,
                default=safe_default,
                key=f"mapping_{category}"
            )
            # Update the assigned_columns based on the selections
            for col in current_mapping:
                if col not in selected_columns and col in st.session_state['assigned_columns']:
                    st.session_state['assigned_columns'].remove(col)
                    st.session_state['refresh_mapping'] = True

            for col in selected_columns:
                if col not in st.session_state['assigned_columns']:
                    st.session_state['assigned_columns'].append(col)
                    st.session_state['refresh_mapping'] = True

            # Update the mapping in session state when there's a change
            st.session_state['mapping'][category] = selected_columns

        if st.button('Update Mapping'):
            set_column_groups()


def show_settings_selection():
    st.write('---')
    st.subheader('Load VVE Configuration File')
    c1, c2 = st.columns([3, 2])
    with c1:
        # show the settings files
        subfiles_settings = [f for f in os.listdir(st.session_state.dir_settings) if os.path.isfile(os.path.join(st.session_state.dir_settings, f))]
        selected_settings_file = st.selectbox("Select a configuration file", subfiles_settings,help=HelpText.splash_config,)
        if selected_settings_file:
            st.session_state.settings_file = os.path.join(st.session_state.dir_settings, selected_settings_file)

        st.write(HelpText.splash_config_explain_1)
        st.markdown(HelpText.splash_config_explain_2)

        # st.subheader("Edit the default.yaml file")
        # edit_default_settings_yaml()
        # edit_mapping()
    with c2:
        st.write(":violet-background[Example configuration `default.yaml` file format for ***mapped*** network drives]")
        st.text(HelpText.splash_config_json_str)

        st.write(":violet-background[Example configuration `default.yaml` file format for saving locally to your computer in the `VoucherVisionEditor/projects/USER/` directory]")
        st.text(HelpText.splash_config_json_str2)

def display_skip_specimen_button():
    if st.session_state.tool_access['show_skip_specimen']:
        st.title('')
        st.markdown('If this specimen is not part of the current transcription workflow, then press the button below. This will mark this specimen as a "skip", place an "X" in the country field, and add it to the "transcribed_skipped.xlsx" file. This cannot be undone.')
        st.button('Skip this specimen and enter no information',key=f"skip_specimen_{group_option}", use_container_width=True, type="secondary",on_click=on_press_skip_specimen)

###############################################################
####################                    #######################
####################    Welcome Page    #######################
####################                    #######################
###############################################################
if 'data' not in st.session_state:
    st.session_state.data = None
if 'data_edited' not in st.session_state:
    st.session_state.data_edited = None

if st.session_state.data is None or not st.session_state.start_editing:
    clear_directory()
    start_server()

    show_header_welcome()

    get_directory_paths(args)

    load_data()

    show_settings_selection()
    # st.markdown(st.session_state.bp_text) ############################################ TODO

    # if st.session_state.start_editing:
    # if st.session_state.data is not None and not st.session_state.start_editing:
        # st.rerun()
def all_but_one_is_one(tracker):
    # Count how many keys have the value of 1
    ones_count = sum(1 for value in tracker.values() if value == 1)
    
    # If all but one key has value 1, the count of 1's should be len(tracker) - 1
    return ones_count == len(tracker) - 1
###############################################################
####################                    #######################
####################      Main App      #######################
####################                    #######################
###############################################################
if st.session_state.start_editing:
    do_print_profiler = False
    if do_print_profiler:
        profiler = cProfile.Profile()
        profiler.enable()

    # with st.expander('table_top', expanded=False):
    #     table_layout('top')

    show_header_main()

    # Initialize previous_row_to_edit if it's not already in session_state
    st.session_state.setdefault('previous_row_to_edit', None)

    # Set the overall layout. Right is for image things, left is for text things
    c_left, c_right, c_help = layout_image_proportion()

    # Organize the text groupings
    group_options = list(st.session_state.grouping.keys()) + ["ALL"]
    group_option = st.session_state.get("group_option", group_options[0])

    group_option_cols = c_left.columns(len(group_options))


    # Layout for Form View (alternative is Spreadsheet View)
    # if st.session_state.view_option == "Form View":

        # Init tracker
    if st.session_state.group_options_tracker == {}:
        for i, option in enumerate(group_options):
            st.session_state.group_options_tracker[option] = 0

    # for finished images
    if 'ALL' in st.session_state.data_edited.loc[st.session_state.row_to_edit, "track_edit"].split(","):
        for i, option in enumerate(group_options):
            if group_option_cols[i].button(option, use_container_width=True, help="Category"):
                st.session_state["group_option"] = option
                group_option = option
    #For in progess images
    else:
        # Create a button for each category group, used for tracking
        for i, option in enumerate(group_options):
            if st.session_state.group_options_tracker[option] == 1:
                if group_option_cols[i].button(option, use_container_width=True, help="Category"):
                    st.session_state["group_option"] = option
                    group_option = option

            elif i <= st.session_state.progress_index:
                if group_option_cols[i].button(option, use_container_width=True, help="Category"):
                    st.session_state["group_option"] = option
                    group_option = option
                
            # elif all_but_one_is_one(st.session_state.group_options_tracker):
            #     if group_option_cols[i].button(option, use_container_width=True):
            #         st.session_state["group_option"] = option
            #         group_option = option
            #         st.session_state.progress_index += 1
            else:
                group_option_cols[i].button(option, use_container_width=True, disabled=True, help="Category")



    with c_left:
        update_progress_bar()
        if (st.session_state.progress == 0) and group_options[0] not in st.session_state.data_edited.loc[st.session_state.row_to_edit, "track_edit"]: 
            # Add default option if "track_edit" is empty and doesn't contain the default option already
            add_default_option_if_not_present()
            st.rerun()
        
        # Create the Previous and Next buttons, define 4 sub columns
        c_index, c_skip ,c_prev, c_next = st.columns([4,4,4,4])
        with c_prev:
            st.button("Previous Img", help="Go back to the previous image",  use_container_width=True, on_click=on_press_previous)

        with c_next:
            # Count the number of group options that have been selected
            # Only enable the 'Next' button if all group options have been selected
            if st.session_state.progress == len(group_options) or st.session_state.access_option == 'Admin':
                st.button("Next Img", help="Cannot move to next image until all categories are unlocked", type="primary", use_container_width=True, on_click=on_press_next, args=[group_options])
            else:
                st.button("Next Img", help="Cannot move to next image until all categories are unlocked", type="primary", use_container_width=True, on_click=on_press_next, args=[group_options],disabled=True)
                # st.info("Please confirm all categories before moving to next image")

        # group_option_cols = c_left.columns(len(group_options))
        # Display a progress bar showing how many of the group_options are present in track_edit
        
                    
        # Get the current row from the spreadsheet, show the index
        n_rows = len(st.session_state.data_edited)
        with c_index:
            # st.write(f"**Image {st.session_state.row_to_edit+1} / {n_rows}**")
            last_true_index_max = st.session_state.data_edited[st.session_state.data_edited["track_view"] == 'True'].index.max() + 1
            if pd.isna(last_true_index_max):
                last_true_index_max = 1
                current_image = 1
                set_value = 1
            else:
                current_image = st.session_state.row_to_edit+1
                set_value = st.session_state.row_to_edit+1
                last_true_index_max = last_true_index_max + 1
            last_true_index_max = int(last_true_index_max)
            try:
                last_val = min([last_true_index_max-1, n_rows])
                skip_to_manual = st.number_input(f"**Image {current_image} / {n_rows}**",
                                                key=f"skip to index{st.session_state.row_to_edit}", 
                                                label_visibility='visible', 
                                                step=1, 
                                                value=set_value, 
                                                min_value=1, 
                                                max_value=last_val)
            except:
                last_val = min([last_true_index_max, n_rows])
                skip_to_manual = st.number_input(f"**Image {current_image} / {n_rows}**",
                                                key=f"skip to index{st.session_state.row_to_edit}1", 
                                                label_visibility='visible', 
                                                step=1, 
                                                value=set_value, 
                                                min_value=1, 
                                                max_value=last_val)
            if skip_to_manual:
                if skip_to_manual != st.session_state.row_to_edit+1:
                    st.session_state.row_to_edit = skip_to_manual-1
                    st.rerun()
        # Create the skip to bookmark button
        with c_skip:
            st.button('Skip ahead',
                        key=f"Skip_to_last_viewed2", 
                        help="Continue from the last processed image in this project",
                        use_container_width=True, 
                        on_click=on_press_skip_to_bookmark)

        display_layout_with_helpers(group_option)
        display_skip_specimen_button()

    # Update the track_view column for the current row
    if st.session_state.access_option != 'Admin': # ONLY add views if in the label tab
        st.session_state.data_edited.loc[st.session_state.row_to_edit, "track_view"] = 'True'
        if st.session_state.data_edited.loc[st.session_state.row_to_edit, "user_uniqname"] == "":
            st.session_state.data_edited.loc[st.session_state.row_to_edit, "user_uniqname"] = st.session_state.user_uniqname

    ### Show the spreadsheet layout
    # elif st.session_state.view_option == "Data Editor":
        # with c_left:
        #     st.write("Skipping ahead (editing in the 'Form View' out of order) will cause issues if all 5 groups are selected while skipping ahead.")
        #     st.write("If skipping ahead, only use the 'ALL' option until returning to sequential editing.")
        #     # Reorder the columns to have "track_view" and "track_edit" at the beginning
        #     reordered_columns = ['user_uniqname', 'user_time_of_edit', 'track_view', 'track_edit', 'track_issues'] + [col for col in st.session_state.data_edited.columns if col not in ['user_uniqname', 'user_time_of_edit', 'track_view', 'track_edit', 'track_issues']]
        #     st.session_state.data_edited = st.session_state.data_edited[reordered_columns]

        #     # If the view option is "Data Editor", create a new full-width container for the editor
        #     with st.container():
        #         edited_data = st.data_editor(st.session_state.data_edited)
        #         b_color = "black"
        #         b_text = "Save Edits"
        #         b_label = f":{b_color}[{b_text}]"
        #         if st.button(label=b_label, type="primary", use_container_width=True):
        #             # Save the edited data back to the session state data
        #             st.session_state.data_edited = edited_data
        #             save_data()

        #         # Slider or number input to select the row
        #         # Only display the slider if there are 2 or more rows
        #         if len(st.session_state.data_edited) >= 2:
        #             slider_value = st.slider("Select a row to display its image", min_value=st.session_state.data_edited.index[0], max_value=st.session_state.data_edited.index[-1], value=int(st.session_state.row_to_edit))

        #             # Only update the row_to_edit if slider value changes
        #             if slider_value != st.session_state.row_to_edit:
        #                 st.session_state.row_to_edit = slider_value
        #             save_data()
                    
        #         # Display the current row
        #         n_rows = len(st.session_state.data_edited)-1
        #         st.write(f"**Showing image for row {st.session_state.row_to_edit} / {n_rows}**")
            # c_gps, c_form = st.columns([4,4])



    



        


    


    # check if the row_to_edit has changed
    if 'last_row_to_edit' not in st.session_state:
        st.session_state['last_row_to_edit'] = None

    # check if the row_to_edit has changed
    if st.session_state.row_to_edit != st.session_state.previous_row_to_edit:
        st.session_state.current_options = []
        st.session_state.previous_row_to_edit = st.session_state.row_to_edit


    # Only load JSON if row has changed
    if c_help:
        with c_help:
            
            load_json_helper_files()

            display_wiki_taxa_main_links()

            # display_wiki_geo_main_links()

            display_coordinates(0)
            
            # display_WFO_partial_match()
            
            # display_wiki_taxa_summary()

            display_conversion_calculator()
            
            display_json_helper_text()

            display_issues()

            display_notes()

            # display_wiki_taxa_sub_links()
            
            # display_search_results()

            if st.session_state.location_google_search == "Hint Panel":
                # display_google_search()        
                pass




        
    ### Display the image
    with c_right:
        image_path_and_load()

        if st.session_state.tool_access.get('ocr'):
            r1, r2, zoom_1, zoom_2, zoom_3, zoom_4, r3, r4 = st.columns([1,1,2,2,2,2,1,1])
        else:
            r1, r2, zoom_1, zoom_2, zoom_3, r3, r4 = st.columns([1,1,2,2,2,1,1])

        if st.session_state.location_google_search == 'Top':
            # display_google_search()
            pass


        con_image = st.container()


        # Add the image to the local server for the zoom functionality

        # Two options for the image viewing buttons
        if st.session_state.tool_access.get('ocr'):
            display_image_options_buttons(st.session_state.relative_path_to_static, zoom_1, zoom_2, zoom_3, zoom_4)
        else:
            display_image_options_buttons(st.session_state.relative_path_to_static, zoom_1, zoom_2, zoom_3, zoom_4=None)
            
        # Display the configurable image viewer
        display_scrollable_image(con_image)

        display_image_rotation_buttons(r1, r2, r3, r4)
        # relative_path_to_static = image_to_server()

    table_layout('bottom')

        


    if st.session_state.location_google_search == 'Bottom':
        # display_google_search()
        pass
    
    if not c_help:
        load_json_helper_files()

        display_wiki_taxa_main_links()

        # display_wiki_geo_main_links()

        display_coordinates(1)
        
        # display_WFO_partial_match()
        
        # display_wiki_taxa_summary()

        display_conversion_calculator()
        
        display_json_helper_text()

        # display_wiki_taxa_sub_links()
        
        # display_search_results()

            

    
    if st.session_state.tool_access.get('additional_info'):
        st.header('Project Progress')
        # col_low_1, col_low_2, col_low_3, col_low_4, col_low_5, col_low_6, col_low_7, col_low_8,  = st.columns([1,1,1,1,1,1,1,1])
        last_true_index, last_fully_viewed, progress_overall_fraction, total_rows = update_progress_bar_overall()
        st.progress(progress_overall_fraction)
        st.write(f"Viewed *{last_true_index+1}* of *{total_rows}* images")
        
        st.header("Additional Project Information")
        display_prompt_template()
    
    display_help()
    

    if do_print_profiler:
        profiler.disable()
        stats = pstats.Stats(profiler).sort_stats('cumulative')
        stats.print_stats(30)