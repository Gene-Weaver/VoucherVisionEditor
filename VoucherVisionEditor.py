import streamlit as st
import pandas as pd
from PIL import Image
import json, os, argparse

# pip install streamlit pandas Pillow openpyxl tk
# Windows
# streamlit run your_script.py -- --save_dir /path/to/save/dir
# Linux
# export SAVE_DIR=/path/to/save/dir && streamlit run your_script.py


st.set_page_config(layout="wide")


# Initialize Streamlit Session State if it hasn't been initialized yet
if "row_to_edit" not in st.session_state:
    st.session_state.row_to_edit = 0

if "data" not in st.session_state:
    st.session_state.data = None

if "file_name" not in st.session_state:
    st.session_state.file_name = None

if "user_input" not in st.session_state:
    st.session_state.user_input = {}

parser = argparse.ArgumentParser(description='Define save location of edited file.')

# Add parser argument for save directory
parser.add_argument('--save-dir', type=str, default=".",
                    help='Directory to save output files')
parser.add_argument('--base-path', type=str, default=".",
                    help='New base path to replace the existing one up to "/Transcription"')

# Parse the arguments
try:
    args = parser.parse_args()
except SystemExit as e:
    # This exception will be raised if --help or invalid command line arguments
    # are used. Currently streamlit prevents the program from exiting normally
    # so we have to do a hard exit.
    os._exit(e.code)

# Get the save directory from the parsed arguments
save_dir = args.save_dir
base_path = args.base_path


# Use save_dir where needed
def save_data():
    # Check the file extension and save to the appropriate format
    if st.session_state.file_name.endswith('.csv'):
        file_path = os.path.join(save_dir, st.session_state.file_name)
        st.session_state.data.to_csv(file_path, index=False)
        st.success('Saved (CSV)')
    elif st.session_state.file_name.endswith('.xlsx'):
        file_path = os.path.join(save_dir, st.session_state.file_name)
        st.session_state.data.to_excel(file_path, index=False)
        st.success('Saved (XLSX)')
    else:
        st.error('Unknown file format.')
def save_data_editor():
    # Check the file extension and save to the appropriate format
    if st.session_state.file_name.endswith('.csv'):
        file_path = os.path.join(save_dir, st.session_state.file_name)
        st.session_state.data.to_csv(file_path, index=False)
    elif st.session_state.file_name.endswith('.xlsx'):
        file_path = os.path.join(save_dir, st.session_state.file_name)
        st.session_state.data.to_excel(file_path, index=False)
    else:
        st.error('Unknown file format.')
def load_data():
    uploaded_file = st.file_uploader("Choose a CSV or Excel file", type=["csv", "xlsx"])
    if uploaded_file is not None:
        if uploaded_file.type == "text/csv":
            st.session_state.data = pd.read_csv(uploaded_file, dtype=str)
            st.session_state.file_name = uploaded_file.name.split('.')[0] + '_edited.csv'
        elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":
            st.session_state.data = pd.read_excel(uploaded_file, dtype=str)
            st.session_state.file_name = uploaded_file.name.split('.')[0] + '_edited.xlsx'
        st.session_state.data = st.session_state.data.fillna('')  # Move this line here
        st.session_state.data['path_to_crop'] = st.session_state.data['path_to_crop'].apply(lambda old_path: replace_base_path(old_path, base_path, 'crop'))
        st.session_state.data['path_to_helper'] = st.session_state.data['path_to_helper'].apply(lambda old_path: replace_base_path(old_path, base_path, 'json'))
        st.session_state.data['path_to_content'] = st.session_state.data['path_to_content'].apply(lambda old_path: replace_base_path(old_path, base_path, 'json'))

def replace_base_path(old_path, new_base_path, opt):
    # print(f"old = {old_path}")
    # print(f"new = {new_base_path}")
    # Replace the base path of the old_path with the new_base_path.
    # Split the path into parts
    parts = old_path.split(os.path.sep)
    # Find the index of the 'Transcription' part
    if opt == 'crop':
        transcription_index = parts.index('Cropped_Images') if 'Cropped_Images' in parts else None
    elif opt == 'json':
        transcription_index = parts.index('Transcription') if 'Transcription' in parts else None

    if transcription_index is not None:
        # Replace the base path up to 'Transcription' with the new_base_path
        new_path = os.path.join(new_base_path, *parts[transcription_index:])
        return new_path
    else:
        return old_path  # Return the old_path unchanged if 'Transcription' is not in the path


# Define pastel colors
color_map = {
    "TAXONOMY": 'blue', 
    "GEOGRAPHY": 'orange', 
    "LOCALITY": 'green',
    "COLLECTING": 'violet', 
    "MISCELLANEOUS": 'red', 
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
        
st.title(':herb: VoucherVision Editor')

if st.session_state.data is None:
    load_data()


if st.session_state.data is not None:
    # Define the four columns
    c1, c2, c3, c4 = st.columns(4)
    view_option = c1.selectbox("Choose a View", ["Form View", "Data Editor"])

    form_col, json_col, image_col = st.columns([1, 1, 2])  


    if view_option == "Form View":

        # Next and previous buttons in first row of form_col
        with form_col:
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Previous"):
                    st.session_state.row_to_edit = max(st.session_state.row_to_edit - 1, st.session_state.data.index[0])
            with col2:
                if st.button("Next"):
                    st.session_state.row_to_edit = min(st.session_state.row_to_edit + 1, st.session_state.data.index[-1])

            # Create a new row for the form
            with st.container():
                # Display the current row
                n_rows = len(st.session_state.data)
                st.write(f"**Editing row {st.session_state.row_to_edit + 1} / {n_rows}**")

                for col in st.session_state.data.columns:
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

            
        
    elif view_option == "Data Editor":
        # Create two columns for the data editor and the image
        # data_editor_col, image_col = st.columns([1, 1])  # Divide the space equally between the two columns

        with form_col:
            edited_data = st.data_editor(st.session_state.data)

            if st.button("Save Edits"):
                # Save the edited data back to the session state data
                st.session_state.data = edited_data
                save_data_editor()

            # Slider or number input to select the row
            slider_value = st.slider("Select a row to display its image", min_value=st.session_state.data.index[0], max_value=st.session_state.data.index[-1], value=st.session_state.row_to_edit)
            
            # Only update the row_to_edit if slider value changes
            if slider_value != st.session_state.row_to_edit:
                st.session_state.row_to_edit = slider_value

            # Display the current row
            n_rows = len(st.session_state.data)-1
            st.write(f"**Editing row {st.session_state.row_to_edit} / {n_rows}**")



    # check if the row_to_edit has changed
    if 'last_row_to_edit' not in st.session_state:
        st.session_state['last_row_to_edit'] = None


    # Only load JSON if row has changed
    with json_col:
        if st.session_state['last_row_to_edit'] != st.session_state.row_to_edit:
            JSON_path = st.session_state.data.loc[st.session_state.row_to_edit, "path_to_helper"]
            if JSON_path:
                with open(JSON_path, "r") as file:
                    print('LOADING JSON')
                    st.session_state['json_dict'] = json.load(file)
                    
        # Display JSON
        if 'json_dict' in st.session_state:
            json_dict = st.session_state['json_dict']

            for key, value in json_dict.items():
                color = color_map_json.get(key, "black")  # Default to black if key is not in color_map
                st.markdown(f"<h4 style='color: {color};'>{key}</h4>", unsafe_allow_html=True)
                for val in value:
                    st.markdown(f"<p style='font-family:times new roman; font-size:20px;'>{val}</p>", unsafe_allow_html=True)  # Use HTML and CSS to style the text


    # Only load image if row has changed
    with image_col:
        if st.session_state['last_row_to_edit'] != st.session_state.row_to_edit:
            st.session_state['image_path'] = st.session_state.data.loc[st.session_state.row_to_edit, "path_to_crop"]
            if pd.notnull(st.session_state['image_path']):
                print('LOADING IMAGE')
                st.session_state['image'] = Image.open(st.session_state['image_path'])
                
        # Display image
        if 'image' in st.session_state and 'image_path' in st.session_state:
            image = st.session_state['image']
            st.image(image, caption=st.session_state['image_path'])


    # update the 'last_row_to_edit' in the session state to the current 'row_to_edit'
    st.session_state['last_row_to_edit'] = st.session_state.row_to_edit

    if st.button('Save Data'):
        save_data()
