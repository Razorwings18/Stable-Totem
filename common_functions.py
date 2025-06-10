from typing import Literal
from tkinter import messagebox
import inspect
import json

def LogEntry(title, message, type: Literal["info", "warning", "error"], show_messagebox=False):
    if show_messagebox:
        if (type=="error"):
            messagebox.showerror(title, message)
        elif (type=="info"):
            messagebox.showinfo(title, message)
        else:
            messagebox.showwarning(title, message)
    print(f"{type} >>> {title}: {message}")

def load_json_from_file(file_path):
    """
    Loads JSON data from file file_path and returns the corresponding dictionary.\n
    Usage:\n
    file_path = "c:\\myJSONfiles\\myJSON.json"\n
    json_data = load_json_from_file(file_path)
    """
    try:
        with open(file_path, "r") as json_file:
            return json.load(json_file)
    except FileNotFoundError:
        print("File not found:", file_path)
    except json.JSONDecodeError:
        print("Invalid JSON format in file:", file_path)
    return {}

def save_json_to_file(file_path, json_dictionary):
    """
    Saves the data in json_dictionary to the JSON file specified in file_path.
    """
    # Convert the updated dictionary to JSON format
    updated_json_data = json.dumps(json_dictionary, indent=4)

    # Write the updated JSON data to a file
    with open(file_path, "w") as output_file:
        output_file.write(updated_json_data)