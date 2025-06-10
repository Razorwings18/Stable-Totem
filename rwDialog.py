import tkinter as tk
from tkinter import filedialog
from typing import List

class _GeneralFunctions:
    def InitializeDialogWindow(self, title: str):
        # This is something that is done for all dialog windows of this script, so it's unified here and called from each of them
        dialog_window_object = tk.Toplevel()
        dialog_window_object.title(title)
        dialog_window_object.resizable(False, False)  # Disable window resizing
        dialog_window_object.grab_set()  # Make the window modal

        dialog_window_object.update_idletasks()  # Ensure dialog window is fully updated

        # Get the coordinates and size of the main window
        main_window = dialog_window_object.master
        main_window.update_idletasks()
        main_window_x = main_window.winfo_rootx()
        main_window_y = main_window.winfo_rooty()
        main_window_width = main_window.winfo_width()
        main_window_height = main_window.winfo_height()

        # Calculate the position for centering the dialog window
        dialog_x = main_window_x + main_window_width // 2 - dialog_window_object.winfo_reqwidth() // 2
        dialog_y = main_window_y + main_window_height // 2 - dialog_window_object.winfo_reqheight() // 2

        # Position the dialog window
        dialog_window_object.geometry(f"+{dialog_x}+{dialog_y}")

        return dialog_window_object

class RestrictiveInputDialog:
    """
    Shows a dialog box where the user can enter a text, restricting the use of disallowed_chars\n
    Usage example:\n
    myPreset = rwDialog.RestrictiveInputDialog("Preset Input", "Enter the preset's name", r'\\/:*?"<>|')()\n\n
    Mind the extra parentheses at the end.
    """

    def __init__(self, title, label, disallowed_chars=""):
        self.title = title
        self.label = label
        self.disallowed_chars = disallowed_chars
        self.output = None
        self.dialog:tk.Toplevel = None
        self.entry = None

    def validate_input(self, text):
        return all(char not in self.disallowed_chars for char in text)

    def create_dialog(self):
        general_functions = _GeneralFunctions()
        self.dialog = general_functions.InitializeDialogWindow(title=self.title)

        label = tk.Label(self.dialog, text=self.label)
        label.pack()

        self.entry = tk.Entry(self.dialog, validate="key")
        self.entry['validatecommand'] = (self.entry.register(self.validate_input), '%P')
        self.entry.pack()
        self.entry.bind("<Return>", lambda event: self.ok_button_clicked())
        self.entry.bind("<Escape>", lambda event: self.cancel_button_clicked())
        self.entry.focus_set()  # Set focus to entry widget

        button_frame = tk.Frame(self.dialog)
        button_frame.pack()

        ok_button = tk.Button(button_frame, text="OK", command=self.ok_button_clicked)
        ok_button.pack(side="left", padx=10, pady=10)

        cancel_button = tk.Button(button_frame, text="Cancel", command=self.cancel_button_clicked)
        cancel_button.pack(side="left", padx=10, pady=10)

        # Add an empty label to center the buttons
        center_label = tk.Label(button_frame)
        center_label.pack(side="left", expand=True, fill="both")

    def ok_button_clicked(self):
        if self.validate_input(self.entry.get()):
            self.output = self.entry.get()
            self.dialog.destroy()

    def cancel_button_clicked(self):
        self.dialog.destroy()

    def __call__(self):
        self.create_dialog()
        self.dialog.wait_window()
        return self.output

class MultiButtonDialog:
    """
    Shows a dialog box that can have many buttons with custom text. Returns the pressed button's name.\n
    Usage example:\n
    myPreset = rwDialog.MultiButtonDialog("Preset selection", "Choose your preset", ["Low Preset", "Medium Preset", "High Preset"])()\n\n
    Mind the extra parentheses at the end.
    """
    def __init__(self, title, label, buttons):
        self.title = title
        self.label = label
        self.buttons = buttons
        self.output = None
        self.dialog:tk.Toplevel = None

    def create_dialog(self):
        general_functions = _GeneralFunctions()
        self.dialog = general_functions.InitializeDialogWindow(title=self.title)

        label = tk.Label(self.dialog, text=self.label)
        label.pack()

        button_frame = tk.Frame(self.dialog)
        button_frame.pack()

        for button in self.buttons:
            dialog_button = tk.Button(button_frame, text=button, command=lambda btn=button: self.button_clicked(btn))
            dialog_button.pack(side="left", padx=10, pady=10)

        # Add an empty label to center the buttons
        center_label = tk.Label(button_frame)
        center_label.pack(side="left", expand=True, fill="both")

    def button_clicked(self, button_name:str):
        self.output = button_name
        self.dialog.destroy()

    def __call__(self):
        self.create_dialog()
        self.dialog.wait_window()
        return self.output

def SelectFolder(target_entry_widget):
    dir = filedialog.askdirectory()
    if (dir != ""):
        target_entry_widget.delete(0, "end")
        target_entry_widget.insert(0, dir)