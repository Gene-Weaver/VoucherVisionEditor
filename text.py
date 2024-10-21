class HelpText():
    splash_config = "This is a .yaml file located in the 'VoucherVisionEditor/settings' folder. Use the template to hide fields, or add new fields for manual data entry."
    splash_config_explain_1 = "You can use the `VoucherVisionEditor/settings/example.yaml` as a template to create a VoucherVisionEditor configuration file. Some of the fields that VoucherVision extracts may not be relevant or require manual revision. Those field names can be added as a list in the `hide_fields` key. The `example.yaml` file shows how to hide the 'order' and 'family' fields."
    splash_config_explain_2 = """We can also add fields that VoucherVision was not instructed to transcribe. 
    Added fields might be those that always require manual entry, or fields that VoucherVision is not capable of transcribing. 
    The `example.yaml` file shows how to add 3 new fields into 2 different categories. 
    Here, `TAXONOMY` is the category and we will add `['subspecies','variety', 'forma']` to the bottom of the existing fields within `TAXONOMY`. 
\n\nThe category can be a new name, it does not have to match the categories set in the prompt .yaml file (e.g. `SLTPvA_long.yaml`). 
    The category `NEW_CATEGORY` will appear as a new tab in the Editor by specifying the Tab name like this:\n\n

\n\n     editor:
        add_fields:
            NEW_CATEGORY:
            - subspecies
            - variety
            - forma
These three new fields will be found in the 'NEW_CATEGORY' Tab instead of the 'TAXONOMY' Tab."""
    splash_config_json = {
        'editor': {
            'hide_fields': ['order', 'family',],
            'add_fields': {
                'TAXONOMY': ['forma','variety'],
                'NEW_CATEGORY': ['anotherFieldName']}
            }
        }
    splash_config_json_str = """editor:
  add_fields:
    TAXONOMY:
    - subspecies
    - variety
    - forma
  hide_fields:
  - order
  - family
  - scientificName
  - speciesNameAuthorship
  - identificationHistory
locations:
  # Edited files will live somewhere like this: S:/VoucherVision/Transcription/UNIQNAME/WORKBENCH_NAME/Transcription/transcribed__edited__2024_10_08T16_40_31.xlsx
  project_dir: ["S:/Curatorial Projects/VoucherVision/Transcription","S:/VoucherVision/Transcription" ]
"""
    splash_config_json_str2 = """editor:
  add_fields:
    TAXONOMY:
    - subspecies
    - variety
    - forma
  hide_fields:
  - order
  - family
  - scientificName
  - speciesNameAuthorship
  - identificationHistory
locations:
  project_dir: 'local'
"""
    

    help_btns = """
:arrow_right_hook: Rotate image 90 degrees counterclockwise\n
:leftwards_arrow_with_hook: Rotate image 90 degrees clockwise\n
'Original' - View full herbarium specimen image\n
'Zoom' - Open curent view in new tab, enables zoom\n
'Collage' - View LeafMachine2 label collage image\n
'OCR' - View OCR confidence scores image\n
:arrow_double_down: Rotate image 180 degrees\n
:arrow_double_up: Rotate image to original position\n
"""

    help_form_btns = """
:eject: Make first letter in field uppercase\n
:arrow_double_down: Make all letters in field lowercase\n
:mag: Launch a Google search for the term in the selected field. Click the button, open the Google search dropdown.\n
:arrow_backward: and :arrow_forward: Accept value from hint. Cannot be reversed/undone. 
You can disable these buttons (using the admin password in the sidebar) and require the user to copy and paste from the Tool Hints to reduce the risk of accidentally accepting incorrect Tool Hints.
"""
    help_form = """
Text input boxes below the 'Tool Hint' header are suggestions based on queries of 3rd-party APIs. 
These values may not be correct, always check before accepting the hint into the official record. 
(The text input for the official record have colored descriptions)\n

"""
    help_specimen = """Text input boxes below the 'Specimen Record' header are the official transcription values 
(the values that were obtained from the OCR and LLMs). 
All edits to these text input boxes will be reflected in the final `transcription__edited__DATETIME.xlsx`spreadsheet.
'Specimen Record' text input boxes have colored descriptions."""

    help_WFO_badge = """If the current specimen's auto-populated taxonomy matches a known entry in World Flora Online, the badge will be :green[green] and say `Exact Match`\n
If the current specimen's auto-populated taxonomy partially matches a known entry in World Flora Online, the badge will be :blue[blue] and say `Partial Match`\n
This badge does not update if you alter text in the input boxes. This is a static value obtained at the time of LLM transcription. 
"""
    help_categories = """Categories are used to organize fields by topic. The fields for each category are mapped in the prompt file (e.g. `SLTPvA_long.yaml`).\n
You can hide some fields by adding the column/field names to the `hide_fields` list in the `./settings/default.yaml` file. You can also specify additional fields beyond 
those that were transcribed by VoucherVision by specifying a Category and field name in the `add_fields` section of the `./settings/default.yaml` file.\n
The 'ALL' category is autogenerated, but all other categories can be modified, so long as it matches the original prompt's mapping.
As the user confirms the values in the form, the next category will unlock. Once you reach `ALL`, you can view all previous categories.\n
The `Next` button will be enabled after all categories are confirmed.
The `Previous` button allows you to view prior images and rework edits.\n
Enabling `Admin` mode allows you to click `Next` without confirming all of the fields.  
"""
    help_hide_tools = """Opening the sidepanel, you will see `Options` and a text entry box. If you enter the admin password, select Admin in the dropdown menu,
then you can hide the following tools to simplify the appearance of the VoucherVisionEditor:
- Display WFO and GEO form hints
- Display move arrow button for form hints (:arrow_backward: and :arrow_forward:)
- Display button to view OCR image
- Display WFO badge
- Display buttons for Wikipedia (taxonomy), POWO, GRIN
- Display top 10 list of WFO taxa (WFO partial matches)
- Display additional project information at page bottom
"""
    LLMTranscription = """This file contains the LLM transcription data. This will be used to create your official records, but will never be modified directly. 
All edits will be stored in a transcribed__DATE.xlsx file."""

    

    TABLECSS = """ 
    <style>
    body {
        background-color: #1e1e1e;
        color: #f5f5f5;
    }
    table.dataTable {
        background-color: #333333;
        color: #f5f5f5;
    }
    table.dataTable thead th {
        background-color: #444444;
        color: #f5f5f5;
    }
    table.dataTable tbody td {
        background-color: #333333;
        color: #f5f5f5;
    }
    table.dataTable tfoot th {
        background-color: #444444;
        color: #f5f5f5;
    }
    table.dataTable tr.even {
        background-color: #2b2b2b;
    }
    table.dataTable tr.odd {
        background-color: #3b3b3b;
    }
    .dataTables_wrapper .dataTables_paginate .paginate_button {
        color: #f5f5f5 !important;
        background-color: #444444 !important;
    }
    .dataTables_wrapper .dataTables_paginate .paginate_button:hover {
        color: #ffffff !important;
        background-color: #666666 !important;
    }
    .dataTables_wrapper .dataTables_length select,
    .dataTables_wrapper .dataTables_filter input {
        background-color: #444444;
        color: #f5f5f5;
    }
    .dataTables_wrapper .dataTables_info {
        color: #f5f5f5;
    }
    .dataTables_wrapper .dataTables_paginate {
        color: #f5f5f5;
    }
    .dataTables_wrapper .dataTables_length {
        color: #f5f5f5;
    }
    .dataTables_wrapper .dataTables_filter label {
        color: #f5f5f5;
    }

    /* Minimize/collapse the index column */
    th:first-child, td:first-child {
        width: 40px !important;
        min-width: 40px !important;
        max-width: 40px !important;
        text-align: center;
    }
    </style>
    """

    
    def __init__(self) -> None:
        pass



