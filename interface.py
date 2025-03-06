import streamlit as st
import requests
import json
import os

# File paths
FIELDS_FILE = "fields_data.json"

# --- Initialize and Load Functions ---

def load_fields(file_name=FIELDS_FILE):
    if os.path.exists(file_name):
        with open(file_name, "r") as f:
            return json.load(f)
    return {
        "background": {"type": "text", "value": "", "example": "e.g., Forest"},
        "faction": {"type": "choice", "value": "vlandian, roman", "example": "e.g., vlandian, roman"}
    }

def save_fields(fields, file_name=FIELDS_FILE):
    with open(file_name, "w") as f:
        json.dump(fields, f)

def initialize_session_state():
    if "fields" not in st.session_state:
        st.session_state["fields"] = load_fields()
    if "dialogue_options" not in st.session_state:
        st.session_state["dialogue_options"] = []
    if "selected_dialogue_options" not in st.session_state:
        st.session_state["selected_dialogue_options"] = {}
    if "debug_mode" not in st.session_state:
        st.session_state["debug_mode"] = False
    if "player_state_selections" not in st.session_state:
        st.session_state["player_state_selections"] = {}
    if "selection_confirmed" not in st.session_state:
        st.session_state["selection_confirmed"] = False
    if "final_dialogue" not in st.session_state:
        st.session_state["final_dialogue"] = ""

# --- Display Functions ---

def display_fields():
    st.header("Game Context and Player Information")
    for field, data in st.session_state["fields"].items():
        if data["type"] == "text":
            data["value"] = st.text_input(f"{field.capitalize()} (Text)", value=data["value"], placeholder=data["example"], key=f"{field}_value")
        elif data["type"] == "choice":
            data["value"] = st.text_input(f"{field.capitalize()} (Choices - separate with commas)", value=data["value"], placeholder=data["example"], key=f"{field}_value")
    save_fields(st.session_state["fields"])

def manage_fields():
    st.sidebar.header("Configure Fields")
    new_field_name = st.sidebar.text_input("Enter new field name")
    field_type = st.sidebar.selectbox("Select field type", ["text", "choice"])
    new_field_example = st.sidebar.text_input("Enter example value for new field")

    if st.sidebar.button("Add Field"):
        if new_field_name:
            if new_field_name in st.session_state["fields"]:
                st.sidebar.warning("Field already exists.")
            else:
                st.session_state["fields"][new_field_name] = {
                    "type": field_type,
                    "value": "",
                    "example": new_field_example
                }
                save_fields(st.session_state["fields"])
                st.sidebar.success(f"Field '{new_field_name}' added as {field_type}.")
        else:
            st.sidebar.warning("Please enter a field name.")

    if st.session_state["fields"]:
        remove_field_name = st.sidebar.selectbox("Select field to remove", options=list(st.session_state["fields"].keys()))
        if st.sidebar.button("Remove Field"):
            if remove_field_name:
                del st.session_state["fields"][remove_field_name]
                save_fields(st.session_state["fields"])
                st.sidebar.success(f"Field '{remove_field_name}' removed!")

    st.sidebar.markdown("---")
    st.session_state["debug_mode"] = st.sidebar.checkbox("Enable Debug Mode", value=st.session_state["debug_mode"])

def request_dialogue_options():
    data_to_send = prepare_data_payload()
    try:
        response = requests.post("http://localhost:5000/generate_dialogue_options", json=data_to_send)
        if response.status_code != 200:
            st.error(f"Failed to send data to API. Status code: {response.status_code}")
        else:
            response_json = response.json()
            st.session_state["dialogue_options"] = response_json.get("dialogue_options", [])
            if st.session_state["debug_mode"]:
                if "debug_info" in response_json:
                    st.write("Debug Information:")
                    st.json(response_json["debug_info"])

    except requests.exceptions.ConnectionError:
        st.error("Failed to connect to the API. Make sure the Flask server is running.")

def prepare_data_payload():
    data = {field: {"type": data["type"], "value": data["value"]} for field, data in st.session_state["fields"].items()}
    data["debug"] = st.session_state["debug_mode"]
    return data

def display_dialogue_options_with_selection():
    st.write("Dialogue Options Generated:")
    for idx, option in enumerate(st.session_state["dialogue_options"]):
        option_key = f"option_{idx}"
        if option_key not in st.session_state["selected_dialogue_options"]:
            st.session_state["selected_dialogue_options"][option_key] = False
        st.session_state["selected_dialogue_options"][option_key] = st.checkbox(option, value=st.session_state["selected_dialogue_options"][option_key])

def display_player_state_selections():
    st.write("Select Options for Player State Fields:")
    for field, data in st.session_state["fields"].items():
        if data["type"] == "choice":
            choices = [option.strip() for option in data["value"].split(",")]
            st.session_state["player_state_selections"][field] = st.selectbox(f"{field.capitalize()} Options", choices)

def submit_selected_dialogues():
    selected_data = {
        "selected_options": [option for idx, option in enumerate(st.session_state["dialogue_options"]) if st.session_state["selected_dialogue_options"][f"option_{idx}"]],
        "debug": st.session_state["debug_mode"]
    }
    try:
        response = requests.post("http://localhost:5000/filter_dialogue_options", json=selected_data)
        if response.status_code != 200:
            st.error(f"Failed to send selection to API. Status code: {response.status_code}")
        else:
            st.session_state["selection_confirmed"] = True
            response_json = response.json()
            if st.session_state["debug_mode"]:
                if "debug_info" in response_json:
                    st.write("Debug Information:")
                    st.json(response_json["debug_info"])
    except requests.exceptions.ConnectionError:
        st.error("Failed to connect to the API. Make sure the Flask server is running.")

def submit_final_player_state():
    # Prepare data with debug mode info if active
    final_selection_data = {**st.session_state["player_state_selections"], "debug": st.session_state["debug_mode"]}
    
    try:
        response = requests.post("http://localhost:5000/confirm_final_dialogue", json=final_selection_data)
        
        if response.status_code != 200:
            st.error(f"Failed to send player state to API. Status code: {response.status_code}")
        else:
            response_json = response.json()
            st.session_state["final_dialogue"] = response_json.get("final_selected_dialogue", "No dialogue generated.")
            
            if st.session_state["debug_mode"]:
                if "debug_info" in response_json:
                    st.write("Debug Information:")
                    st.json(response_json["debug_info"])
                
    except requests.exceptions.ConnectionError:
        st.error("Failed to connect to the API. Make sure the Flask server is running.")


# --- Main Streamlit App ---

initialize_session_state()
manage_fields()
display_fields()

# Button to request dialogue generation
if st.button("Generate Dialogue Options"):
    request_dialogue_options()

# Display generated dialogue options with checkboxes for selection
if st.session_state["dialogue_options"]:
    display_dialogue_options_with_selection()
    if st.button("Confirm Selected Dialogues"):
        submit_selected_dialogues()
        
    # Display player state options after confirming selected dialogues
    if st.session_state["selection_confirmed"]:
        display_player_state_selections()
        if st.button("Submit Final Player State"):
            submit_final_player_state()

        # Display the final dialogue after processing player state
        if st.session_state["final_dialogue"]:
            st.subheader("Final Selected Dialogue:")
            st.write(f"**{st.session_state['final_dialogue']}**")
