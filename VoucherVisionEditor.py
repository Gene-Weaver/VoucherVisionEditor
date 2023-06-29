import streamlit as st
import pandas as pd
import json, os, argparse, shutil, re, toml
import subprocess
import threading
from PIL import Image
from utils import *
# pip install streamlit pandas Pillow openpyxl streamlit-aggrid
# Windows
# streamlit run your_script.py -- --SAVE_DIR /path/to/save/dir
# Linux
# export SAVE_DIR=/path/to/save/dir && streamlit run your_script.py


### To run:
# streamlit run VoucherVisionEditor.py -- 
# --save-dir D:/Dropbox/LM2_Env/VoucherVision_Output/Compare_Set/chatGPT_prompt-V1_2023_06_12__18-11-40/Transcription
# --base-path C:/Users/uname/new_location
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
        # After uploading and processing the data, setup the config
        setup_streamlit_config(mapbox_key)


        if uploaded_file.type == "text/csv":
            st.session_state.data = pd.read_csv(uploaded_file, dtype=str)
            st.session_state.file_name = uploaded_file.name.split('.')[0] + '_edited.csv'
        elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":
            st.session_state.data = pd.read_excel(uploaded_file, dtype=str)
            st.session_state.file_name = uploaded_file.name.split('.')[0] + '_edited.xlsx'
        st.session_state.data = st.session_state.data.fillna('')  # Move this line here
        
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
    clear_directory(static_folder_path)
    # Ensure the server is run in a separate thread so it doesn't block the Streamlit app
    def target():
        subprocess.run(["python", "-m", "http.server"], cwd=static_folder_path, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    threading.Thread(target=target).start()


def clear_directory(directory_path):
    for root, dirs, files in os.walk(directory_path):
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

# Define pastel colors
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

#### Welcome Page

if 'data' not in st.session_state:
    st.session_state.data = None

if st.session_state.data is None:
    # Create three columns
    h1, h2, h3 = st.columns([2,1,2])
    # Use the second (middle) column for the logo
    with h2:
        st.image("img/logo.png", use_column_width=True)
    # Use markdown with HTML to center text
    st.markdown("<h1 style='text-align: center;'>VoucherVision Editor</h1>", unsafe_allow_html=True)

    get_directory_paths(args)
    mapbox_key = prompt_for_mapbox_key()
    load_data(mapbox_key)
    start_server()

    if st.session_state.data is not None:
        st.experimental_rerun()

### Main App
if st.session_state.data is not None:
    # Create two columns for the logo and the title
    h1, h2, h3 = st.columns([2,3,1])

    # Use the first column for the logo and the second for the title
    with h1:
        st.image("img/logo.png", width=200)  # adjust width as needed

    with h2:
        st.title('VoucherVision Editor')

    # print(f"HERE: {st.session_state.SAVE_DIR}")
    # Get the directory of the current file 
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # Create the path to the new 'static' directory
    static_folder_path = os.path.join(current_dir, 'static')
    # Create 'static' directory
    os.makedirs(static_folder_path, exist_ok=True)
    static_folder_path_o = os.path.join(static_folder_path, "static_og")
    static_folder_path_c = os.path.join(static_folder_path, "static_cr")
    os.makedirs(static_folder_path_o, exist_ok=True)
    os.makedirs(static_folder_path_c, exist_ok=True)


    # Define the four columns
    c1, c3, c4, c5 = st.columns([4,2,1,1])
    # group_option = c1.selectbox("Choose a Category", list(grouping.keys()) + ["ALL"])
    group_options = list(grouping.keys()) + ["ALL"]
    group_option = st.session_state.get("group_option", group_options[0])

    group_option_cols = c1.columns(len(group_options))

    for i, option in enumerate(group_options):
        if group_option_cols[i].button(option):
            st.session_state["group_option"] = option
            group_option = option

    image_option = c3.selectbox('Choose an Image', ['Cropped', 'Original'])
    view_option = c4.selectbox("Choose a View", ["Form View", "Data Editor"])
    img_loc = c5.selectbox("Image Position", ["Right", "Middle"])

    if img_loc == 'Middle':
        form_col, image_col, json_col  = st.columns([1, 2, 1])  
    elif img_loc == 'Right':
        form_col, json_col, image_col  = st.columns([1, 1, 2])  



    if view_option == "Form View":

        # Next and previous buttons in first row of form_col
        with form_col:
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Previous"):
                    if st.session_state.row_to_edit == st.session_state.data.index[0]:
                        st.session_state.row_to_edit = st.session_state.data.index[-1]
                    else:
                        st.session_state.row_to_edit -= 1
            with col2:
                if st.button("Next"):
                    if st.session_state.row_to_edit == st.session_state.data.index[-1]:
                        st.session_state.row_to_edit = st.session_state.data.index[0]
                    else:
                        st.session_state.row_to_edit += 1


            # Create a new row for the form
            with st.container():
                # Display the current row
                n_rows = len(st.session_state.data)
                st.write(f"**Editing row {st.session_state.row_to_edit + 1} / {n_rows}**")

                # for col in st.session_state.data.columns:
                columns_to_show = st.session_state.data.columns if group_option == "ALL" else grouping[group_option]
                for col in columns_to_show:
                    # Find the corresponding group and color
                    for group, fields in grouping.items():
                        if col in fields:
                            color = color_map.get(group, "#FFFFFF")  # default to white color
                            break
                    else:
                        color = color_map.get("MISCELLANEOUS", "#FFFFFF")  # default to white color

                    colored_label = f":{color}[{col}]"
                    st.session_state.user_input[col] = st.text_input(colored_label, st.session_state.data.loc[st.session_state.row_to_edit, col], key=col)
                    if st.session_state.user_input[col] != st.session_state.data.loc[st.session_state.row_to_edit, col]:
                        st.session_state.data.loc[st.session_state.row_to_edit, col] = st.session_state.user_input[col]
                        save_data()
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


    elif view_option == "Data Editor":
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
                slider_value = st.slider("Select a row to display its image", min_value=st.session_state.data.index[0], max_value=st.session_state.data.index[-1], value=st.session_state.row_to_edit)

                # Only update the row_to_edit if slider value changes
                if slider_value != st.session_state.row_to_edit:
                    st.session_state.row_to_edit = slider_value

            # Display the current row
            n_rows = len(st.session_state.data)-1
            st.write(f"**Showing image for row {st.session_state.row_to_edit} / {n_rows}**")

        # Create separate columns for image and JSON as they are below the editor in this case
        if img_loc == 'Middle':
            image_col, json_col  = st.columns([1, 1])  
        elif img_loc == 'Right':
            json_col, image_col  = st.columns([1, 1]) 


    # check if the row_to_edit has changed
    if 'last_row_to_edit' not in st.session_state:
        st.session_state['last_row_to_edit'] = None


    # Only load JSON if row has changed
    with json_col:
        if st.session_state['last_row_to_edit'] != st.session_state.row_to_edit:
            JSON_path = st.session_state.data.loc[st.session_state.row_to_edit, "path_to_helper"]
            # print(f"JSON_path === {st.session_state.row_to_edit}")

            # print(f"JSON_path === {JSON_path}")
            if JSON_path:
                with open(JSON_path, "r") as file:
                    # print('LOADING JSON')
                    st.session_state['json_dict'] = json.load(file)
                    
        # Display JSON
        if 'json_dict' in st.session_state:
            json_dict = st.session_state['json_dict']

            for main_key, main_value in json_dict.items():
                if group_option == 'ALL':
                    color = color_map_json.get(main_key, "black")  # Default to black if key is not in color_map
                    st.markdown(f"<h4 style='color: {color};'>{main_key}</h4><br>", unsafe_allow_html=True)
                    if isinstance(main_value, dict):
                        for sub_key, sub_value in main_value.items():
                            if sub_value:
                                st.markdown(f"<b style='font-size:20px;'>{sub_key}: <br></b> {sub_value}<br>", unsafe_allow_html=True)
                elif (main_key == group_option) or (main_key == 'MISCELLANEOUS'):
                    color = color_map_json.get(main_key, "black")  # Default to black if key is not in color_map
                    st.markdown(f"<h4 style='color: {color};'>{main_key}</h4><br>", unsafe_allow_html=True)
                    if isinstance(main_value, dict):
                        for sub_key, sub_value in main_value.items():
                            if sub_value:
                                sub_value_show = remove_number_lines(sub_value)
                                sub_value_show = sub_value_show.replace('\n', '<br/>')
                                st.markdown(f"<b style='font-size:20px;'>{sub_key}: <br></b> {sub_value_show}<br>", unsafe_allow_html=True)

        
        # After displaying the first JSON...
        if st.session_state['last_row_to_edit'] != st.session_state.row_to_edit:
            # Load second JSON (OCR)
            original_JSON_path = st.session_state.data.loc[st.session_state.row_to_edit, "path_to_helper"]
            # print(original_JSON_path)
            
            if original_JSON_path:
                # Breakdown the path into parts
                path_parts = original_JSON_path.split(os.path.sep)
                
                # Change the last directory name to 'Individual_OCR'
                path_parts[-2] = 'Individual_OCR'
                
                # Combine the parts back together
                OCR_JSON_path = os.path.sep.join(path_parts)
                # print(OCR_JSON_path)
                
                # Check if the file exists
                if os.path.isfile(OCR_JSON_path):
                    with open(OCR_JSON_path, "r") as file:
                        st.session_state['OCR_JSON'] = json.load(file)  # Save JSON data, not the path

        # Display OCR JSON
        if 'OCR_JSON' in st.session_state:
            OCR_JSON = st.session_state['OCR_JSON']
            # print(OCR_JSON)
            # Assuming the JSON structure is like { "OCR": "Some Text" }
            color = color_map.get('OCR', "#FFFFFF") 
            st.markdown(f"<h4 style='color: {color};'>All OCR Text</h4><br>", unsafe_allow_html=True)
            cleaned_OCR_text = remove_number_lines(OCR_JSON['OCR'])
            OCR_show = cleaned_OCR_text.replace('\n', '<br/>')
            st.markdown(f"""<p style='font-size:20px;'>{OCR_show}</p><br>""", unsafe_allow_html=True)




    with image_col:
        if st.session_state['last_row_to_edit'] != st.session_state.row_to_edit or 'last_image_option' not in st.session_state or st.session_state['last_image_option'] != image_option:
            if image_option == 'Original':
                st.session_state['image_path'] = st.session_state.data.loc[st.session_state.row_to_edit, "path_to_original"]
            elif image_option == 'Cropped':
                st.session_state['image_path'] = st.session_state.data.loc[st.session_state.row_to_edit, "path_to_crop"]
            if pd.notnull(st.session_state['image_path']):
                new_img_path = st.session_state['image_path']
                new_img_path_fname = os.path.basename(new_img_path)
                print(f'LOADING IMAGE: {new_img_path_fname}')
                st.session_state['image'] = Image.open(new_img_path)
            # Remember the selected image option
            st.session_state['last_image_option'] = image_option

        ### FOR VS CODE
        # if 'image' in st.session_state and 'last_image_option' in st.session_state:            
                    
            # if st.session_state['last_image_option'] == 'Original':
            #     static_image_path = os.path.join(static_folder_path_o, os.path.basename(st.session_state['image_path']))
            # elif st.session_state['last_image_option'] == 'Cropped':
            #     static_image_path = os.path.join(static_folder_path_c, os.path.basename(st.session_state['image_path']))
            
            # shutil.copy(st.session_state["image_path"], static_image_path)

            # # Create the HTML hyperlink with the image
            # relative_path_to_static = os.path.relpath(static_image_path, current_dir).replace('\\', '/')
            # print(relative_path_to_static)
            # st.markdown(f'[**Zoom**](/app/{os.path.join(current_dir, relative_path_to_static)})', unsafe_allow_html=True)


            # # Display the image
            # image = st.session_state['image']
            # st.image(image, caption=st.session_state['image_path'])
        ### FOR TERMINAL
        if 'image' in st.session_state and 'last_image_option' in st.session_state:            
            # static_folder_path = os.path.join(current_dir, 'static')

            if st.session_state['last_image_option'] == 'Original':
                static_image_path = os.path.join('static_og', os.path.basename(st.session_state['image_path']))
                shutil.copy(st.session_state["image_path"], os.path.join(static_folder_path_o, os.path.basename(st.session_state['image_path'])))
            elif st.session_state['last_image_option'] == 'Cropped':
                static_image_path = os.path.join('static_cr', os.path.basename(st.session_state['image_path']))
                shutil.copy(st.session_state["image_path"], os.path.join(static_folder_path_c, os.path.basename(st.session_state['image_path'])))
            
            
            # if st.session_state['last_image_option'] == 'Original':
            #     static_image_path = os.path.join('static_og', os.path.basename(st.session_state['image_path']))
            # elif st.session_state['last_image_option'] == 'Cropped':
            #     static_image_path = os.path.join('static_cr', os.path.basename(st.session_state['image_path']))
            
            # shutil.copy(st.session_state["image_path"], static_image_path)

            # Create the HTML hyperlink with the image
            relative_path_to_static = os.path.relpath(static_image_path, current_dir).replace('\\', '/')
            print(f"Adding to Zoom image sever: {relative_path_to_static}")
            st.markdown(f'[**Zoom**](http://localhost:8000/{relative_path_to_static})', unsafe_allow_html=True)

            # Display the image
            image = st.session_state['image']
            st.image(image, caption=st.session_state['image_path'])






    # update the 'last_row_to_edit' in the session state to the current 'row_to_edit'
    st.session_state['last_row_to_edit'] = st.session_state.row_to_edit

    if st.button('Save Data'):
        save_data()
