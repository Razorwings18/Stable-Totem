import customtkinter as ctk
import rwCTk
import rwDialog
import rwCTk as rwctk
import json, os, glob, time
from tkinter import messagebox
from typing import Literal

# Path where the presets will be saved
_preset_path = ""

def Initialize(script_path: str):
    global _preset_path
    _preset_path = f"{script_path}\\files\\TTI_presets"

def PromptPresetNew(preset_file_menu:ctk.CTkOptionMenu, preset_prompt_buttons, negative_preset_prompt_buttons, selected_preset = ""):
    # This process creates a new prompt preset file
    
    if (len(preset_prompt_buttons)>0) or (len(negative_preset_prompt_buttons)>0):
        preset_dialog_preamble = "This will create a new preset with the positive and negative prompt presets as they are currently entered.\n\nEnter the new preset's name:"
        #preset_save_name = simpledialog.askstring("Enter New Preset Name", preset_dialog_preamble)
        preset_save_name = rwDialog.RestrictiveInputDialog("Enter New Preset Name", preset_dialog_preamble, r'\\/:*?"<>|')()
        
        # Save the JSON file
        if (preset_save_name != None) and (preset_save_name != ""):
            SavePresetJSON(preset_save_name= preset_save_name, preset_prompt_buttons= preset_prompt_buttons, negative_preset_prompt_buttons= negative_preset_prompt_buttons)
            
            # Populate the preset list
            PopulatePresetFilesList(preset_file_menu=preset_file_menu, selected_preset = selected_preset)

def PromptPresetSave(preset_prompt_buttons, negative_preset_prompt_buttons, selected_preset = ""):
    # This overwrites the selected preset with the current preset values
    
    if (len(preset_prompt_buttons)>0) or (len(negative_preset_prompt_buttons)>0):
        if (selected_preset != ""):
            result = messagebox.askyesno("Confirmation", f"Are you sure that you want to overwrite \"{selected_preset}\" with the new preset values?",
                                         icon = "warning")
            
            if result:
                SavePresetJSON(preset_save_name=selected_preset, preset_prompt_buttons= preset_prompt_buttons, negative_preset_prompt_buttons= negative_preset_prompt_buttons)

def SavePresetJSON(preset_save_name, preset_prompt_buttons, negative_preset_prompt_buttons):
    # preset_save_name must have been checked for empty before calling this methods

    data = {
        "prompt_preset": [],
        "negative_prompt_preset": []
    }

    # Process preset_prompt_buttons
    for button in preset_prompt_buttons:
        button_info = {
            "prompt": button._text,
            "priority": button.priority
        }
        data["prompt_preset"].append(button_info)

    # Process negative_preset_prompt_buttons
    for button in negative_preset_prompt_buttons:
        button_info = {
            "prompt": button._text,
            "priority": button.priority
        }
        data["negative_prompt_preset"].append(button_info)

    # Define the filename for the JSON file
    preset_save_name = _preset_path + "\\" + preset_save_name + ".json"

    # Write the button information to the JSON file
    with open(preset_save_name, "w") as file:
        json.dump(data, file)

def PopulatePresetFilesList(preset_file_menu: ctk.CTkOptionMenu, selected_preset = None):
        # This process fills the Option control with all existing preset files
        myPath = _preset_path
        preset_list = []

        # Search for JSON files in the path
        json_files = glob.glob(os.path.join(myPath, "*.json"))

        # Extract filenames without extension
        for file in json_files:
            filename = os.path.splitext(os.path.basename(file))[0]
            preset_list.append(filename)

        # Print the list of filenames
        preset_file_menu.configure(values=preset_list)
        if (selected_preset != None):
            preset_file_menu.set(selected_preset)
        else:
            preset_file_menu.set("")
        #print(preset_list)

def PromptPresetLoad(caller, preset_save_name: str):
    # Since we can't import TotemGUI due to circular reference, make a "mini-cast" here
    from GUI import TotemGUI
    structured_caller:TotemGUI = caller
    
    if preset_save_name != "":
        # If there are preset strings already loaded, check if the user wants to append to, or replace them.
        if (len(structured_caller._preset_prompt_canvas.buttons)>0) or (len(structured_caller._preset_negative_prompt_canvas.buttons)>0):
            result = rwDialog.MultiButtonDialog("Append or replace?", "Do you want to append this preset to the currently-loaded preset texts\n or to completely replace them with this preset?",
                                                buttons=["Append", "Replace", "Cancel"])()
            if result == "Replace":
                structured_caller._preset_prompt_canvas.clear()
                structured_caller._preset_negative_prompt_canvas.clear()
            elif result == "Cancel" or result == None:
                return

        # Define the filename for the JSON file
        preset_save_name = _preset_path + "\\" + preset_save_name + ".json"

        # Load the data from the JSON file
        with open(preset_save_name, "r") as file:
            data = json.load(file)

        # Retrieve the button information from the loaded data
        prompt_preset = data["prompt_preset"]
        negative_prompt_preset = data["negative_prompt_preset"]

        # Process prompt_preset
        for button_info in prompt_preset:
            prompt = button_info["prompt"]
            priority = button_info["priority"]
            # Load the preset positive prompt buttons
            AddPresetPrompt(structured_caller, prompt, structured_caller._preset_prompt_canvas, "positive", priority)

        # Process negative_prompt_preset
        for button_info in negative_prompt_preset:
            prompt = button_info["prompt"]
            priority = button_info["priority"]
            # Load the preset negative prompt buttons
            AddPresetPrompt(structured_caller, prompt, structured_caller._preset_negative_prompt_canvas, "negative", priority)

def PromptDelete(preset_file_menu:ctk.CTkOptionMenu, preset_to_delete:str):
    # This process creates a new prompt preset file
    
    if (preset_to_delete != None) and (preset_to_delete != ""):
        preset_dialog_preamble = f"Are you positive that you want to delete preset {preset_to_delete}?\nEnter the word 'yes' to delete it."
        confirmation = rwDialog.RestrictiveInputDialog("Delete preset", preset_dialog_preamble, r'\\/:*?"<>|')()
        
        # Save the JSON file
        if (confirmation != None):
            if (confirmation.lower() == "yes"):
                delete_path = _preset_path + "\\" + preset_to_delete + ".json"
                os.remove(delete_path)

                # Wait until the file is actually deleted before trying to populate the Option control
                while os.path.exists(delete_path):
                    time.sleep(0.1)

                # Populate the preset list
                PopulatePresetFilesList(preset_file_menu=preset_file_menu)

def ClearPresets(canvas:rwCTk.rwCTk_ButtonCanvas):
    if len(canvas.buttons) > 0:
        result = messagebox.askyesno("Confirmation", "Clear all presets?", icon = "warning")
        
        if result:
            canvas.clear()

def AddPresetPromptFromGUI(caller, preset_entry_object: ctk.CTkEntry, preset_canvas: rwctk.rwCTk_ButtonCanvas, 
                        target_canvas: Literal["positive", "negative"]):
    """
    This process mainly calls _AddPresetPrompt but adds some actions for when it is called directly from the GUI.
    """
    # Since we can't import TotemGUI due to circular reference, make a "mini-cast" here
    from GUI import TotemGUI
    structured_caller:TotemGUI = caller

    # Add the prompt button
    AddPresetPrompt(structured_caller, preset_entry_object.get(), preset_canvas, target_canvas)
    
    # Clear the contents of the entry control
    if len(preset_entry_object.get().strip().lower())>0:
        preset_entry_object.delete(0, 'end')
    

def AddPresetPrompt(caller, preset_string: str, preset_canvas: rwctk.rwCTk_ButtonCanvas, 
                        target_canvas: Literal["positive", "negative"], priority=0):
    """
    This process adds a button either to the preset prompt or to the negative preset prompt canvas\n
    It is used for both since both of them work almost exactly the same
    """
    # Since we can't import TotemGUI due to circular reference, make a "mini-cast" here
    from GUI import TotemGUI
    structured_caller:TotemGUI = caller

    preset_prompt_string = preset_string.strip().lower()
    if len(preset_prompt_string)>0:
        # First, let's make sure that this has not already been added to the list
        for button in preset_canvas.buttons:
            if button._text == preset_prompt_string:
                # A button with that text already exists in the list. Do nothing.
                break
        else:
            # A button with that text was not found, so we'll add a new one.
            if target_canvas == "positive":
                left_click_function = structured_caller._PresetPromptLeftClick
                right_click_function = structured_caller._PresetPromptRightClick
            else:
                left_click_function = structured_caller._PresetNegativePromptLeftClick
                right_click_function = structured_caller._PresetNegativePromptRightClick

            newButton = preset_canvas.add_button(button_text=preset_prompt_string, leftclick_command=left_click_function, rightclick_command=right_click_function)
            
            # Add a "priority" property to the new button. This will be the weight of this string in the prompt.
            newButton.priority = priority
            structured_caller._UpdatePresetButtonColors(newButton)
            
            # Force the canvas to scroll to the end in order to show the button we just created
            preset_canvas.ScrollToEnd()