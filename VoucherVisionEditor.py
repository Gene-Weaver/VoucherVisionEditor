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
parser.add_argument('--base-path', type=str, default='',
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

        if base_path != '':
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
                    st.session_state.row_to_edit = max(st.session_state.row_to_edit - 1, st.session_state.data.index[0])
            with col2:
                if st.button("Next"):
                    st.session_state.row_to_edit = min(st.session_state.row_to_edit + 1, st.session_state.data.index[-1])

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

            
        
    elif view_option == "Data Editor":
        # Create two columns for the data editor and the image
        # data_editor_col, image_col = st.columns([1, 1])  # Divide the space equally between the two columns

        # with form_col:
        #     edited_data = st.data_editor(st.session_state.data)

        #     if st.button("Save Edits"):
        #         # Save the edited data back to the session state data
        #         st.session_state.data = edited_data
        #         save_data_editor()

        #     # Slider or number input to select the row
        #     slider_value = st.slider("Select a row to display its image", min_value=st.session_state.data.index[0], max_value=st.session_state.data.index[-1], value=st.session_state.row_to_edit)
            
        #     # Only update the row_to_edit if slider value changes
        #     if slider_value != st.session_state.row_to_edit:
        #         st.session_state.row_to_edit = slider_value

        #     # Display the current row
        #     n_rows = len(st.session_state.data)-1
        #     st.write(f"**Editing row {st.session_state.row_to_edit} / {n_rows}**")
        # If the view option is "Data Editor", create a new full-width container for the editor
        with st.container():
            edited_data = st.data_editor(st.session_state.data)

            if st.button("Save Edits"):
                # Save the edited data back to the session state data
                st.session_state.data = edited_data
                save_data_editor()

            # Slider or number input to select the row
            # Only display the slider if there are 2 or more rows
            if len(st.session_state.data) >= 2:
                slider_value = st.slider("Select a row to display its image", min_value=st.session_state.data.index[0], max_value=st.session_state.data.index[-1], value=st.session_state.row_to_edit)

                # Only update the row_to_edit if slider value changes
                if slider_value != st.session_state.row_to_edit:
                    st.session_state.row_to_edit = slider_value

            # Display the current row
            n_rows = len(st.session_state.data)-1
            st.write(f"**Editing row {st.session_state.row_to_edit} / {n_rows}**")

            
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
            print(f"JSON_path === {st.session_state.row_to_edit}")

            print(f"JSON_path === {JSON_path}")
            if JSON_path:
                with open(JSON_path, "r") as file:
                    print('LOADING JSON')
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
                                st.markdown(f"<b style='font-size:20px;'>{sub_key}: <br></b> {sub_value}<br>", unsafe_allow_html=True)



    # # Only load image if row has changed
    # with image_col:
    #     if st.session_state['last_row_to_edit'] != st.session_state.row_to_edit:
    #         st.session_state['image_path'] = st.session_state.data.loc[st.session_state.row_to_edit, "path_to_original"]
    #         st.session_state['image_path'] = st.session_state.data.loc[st.session_state.row_to_edit, "path_to_crop"]
    #         if pd.notnull(st.session_state['image_path']):
    #             print('LOADING IMAGE')
    #             st.session_state['image'] = Image.open(st.session_state['image_path'])
                
    #     # Display image
    #     if 'image' in st.session_state and 'image_path' in st.session_state:
    #         image = st.session_state['image']
    #         st.image(image, caption=st.session_state['image_path'])
    # Only load image if row has changed
    with image_col:

        # Add a selectbox for the image selection

        if st.session_state['last_row_to_edit'] != st.session_state.row_to_edit or 'last_image_option' not in st.session_state or st.session_state['last_image_option'] != image_option:
            if image_option == 'Original':
                st.session_state['image_path'] = st.session_state.data.loc[st.session_state.row_to_edit, "path_to_original"]
            elif image_option == 'Cropped':
                st.session_state['image_path'] = st.session_state.data.loc[st.session_state.row_to_edit, "path_to_crop"]

            if pd.notnull(st.session_state['image_path']):
                print('LOADING IMAGE')
                st.session_state['image'] = Image.open(st.session_state['image_path'])
                
            # Remember the selected image option
            st.session_state['last_image_option'] = image_option

        # Display image
        if 'image' in st.session_state and 'image_path' in st.session_state:
            image = st.session_state['image']
            st.image(image, caption=st.session_state['image_path'])



    # update the 'last_row_to_edit' in the session state to the current 'row_to_edit'
    st.session_state['last_row_to_edit'] = st.session_state.row_to_edit

    if st.button('Save Data'):
        save_data()
