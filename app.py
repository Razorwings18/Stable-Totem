import os
from GUI import TotemGUI

script_path = os.path.dirname(os.path.abspath(__file__)) # Get the path of the Python script
totem_GUI = TotemGUI(script_path)

# Create app user interface
totem_GUI.GenerateBaseGUI()