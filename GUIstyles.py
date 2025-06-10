"""
Used to create widgets with a standardized look & feel
"""

import rwCTk as rwctk
import customtkinter as ctk 
import tkinter as tk
import re
from typing import Literal

# These are widgets with a standardized look & feel
######################## TOP BAR ##########################
def topbar_menu_frame(master, height=0, width=0, fg_color="Black"):
    return ctk.CTkFrame(master, height=height, width=width, fg_color=fg_color, border_width=0)

def topbar_navigation_button(master, height=0, width=0, text="", image=None, border_width=0, corner_radius=0, command=None):
    return ctk.CTkButton(master, height=height, width=width, text=text, image=image, corner_radius=corner_radius,
                                         font=("Arial Narrow", 20), border_width=border_width, command=command, fg_color="Black", 
                                         hover_color="#4b2d17", text_color="#ab8e6d")

def topbar_selectbutton(master, initvalue, values):
    mainmenu_selectbutton_var = ctk.StringVar(value=initvalue)
    #FG_COLOR #211a15
    return ctk.CTkSegmentedButton(master, values=values, variable=mainmenu_selectbutton_var, font=("Arial Narrow", 20), 
                                  fg_color="Black", unselected_color="Black", selected_color="#4b2d17", 
                                  selected_hover_color="#4b2d17", unselected_hover_color="#35281f",
                                  text_color="#ab8e6d")


######################## LEFT MENU ########################
class mainmenu_inner_label():
    def __init__(self, master, text="") -> None:
        self.element = ctk.CTkLabel(master, text=text, font=("Arial", 9), text_color="white")

class mainmenu_inner_entry():
    def __init__(self, master, width, placeholder_text = "", starting_text = "", disallowed_chars = "", allowed_chars = "") -> None:
        self.element = ctk.CTkEntry(master, width=width, font=("Arial", 10), placeholder_text=placeholder_text,
                                   text_color="white", fg_color="#515151", height=15)
        
        if (disallowed_chars != "") or (allowed_chars != ""):
            self.disallowed_chars = disallowed_chars
            self.allowed_chars = allowed_chars
            self.element.bind("<Key>", self.validate_input) # validate="key" is not working on CTkEntry, so we'll do it manually
        self.element.bind("Tab", self.tab_handler)
        
        if len(starting_text)>0:
            self.element.insert(0, starting_text)
    
    def tab_handler(self, event):
        if event.state & 1:
            # Shift-Tab pressed. Shift-Tab doesn't do anything in the Entry, so we'll just let it slide.
            return
        else:
            # Tab pressed. Tab does add a Tab in the Entry, so we'll force the re-focus and prevent Tab from taking effect here.
            event.widget.tk_focusNext().focus()
        return "break"
    
    def validate_input(self, event):
        if event.keysym == 'BackSpace' or event.keysym == 'Tab':
            return
    
        # Now we'll check whether adding the character event.char results in a disallowed or in an allowed regular expression
        if (event.char) != "":
            char_entry_allowed = True
            
            if (self.disallowed_chars != ""):
                char_entry_allowed = re.match(self.disallowed_chars, self.element.get() + event.char) == None
            
            if (self.allowed_chars != "") and (char_entry_allowed):
                char_entry_allowed = re.match(self.allowed_chars, self.element.get() + event.char) != None
            
            if (not char_entry_allowed):
                return "break"
    
class mainmenu_inner_textbox():
    def __init__(self, master, width, height, wrap="word") -> None:
        self.element = ctk.CTkTextbox(master, width=width, height=height, font=("Arial", 10),
                                   text_color="white", fg_color="#515151", wrap=wrap)

class mainmenu_button_contour():
    def __init__(self, master, height=0, width=0, text="", image=None, border_width=0, corner_radius=0, command=None) -> None:
        self.element = ctk.CTkButton(master, height=height, width=width, text=text, image=image, corner_radius=corner_radius,
                                         font=("Arial", 10), border_width=border_width, command=command, fg_color="transparent",
                                         text_color="white", hover_color="#b08c5f")

def mainmenu_button(master, height=0, width=0, text="", image=None, border_width=0, corner_radius=0, command=None):
    return ctk.CTkButton(master, height=height, width=width, text=text, image=image, corner_radius=corner_radius,
                                         font=("Arial", 10), border_width=border_width, command=command, fg_color="#7c6548", hover_color="#b08c5f")

def mainmenu_frame(master, height=0, width=0, fg_color="#353535"):
    return ctk.CTkFrame(master, height=height, width=width, fg_color=fg_color, border_width=0)

def mainmenu_subframe(master, border_width=0):
    return ctk.CTkFrame(master, height=0, width=0, fg_color="#353535", border_width=border_width, border_color="#4d4d4d")

class mainmenu_switch():
    def __init__(self, master, text, initvalue, onvalue, offvalue) -> None:
        mainmenu_switch_var = ctk.StringVar(value=initvalue)
        self.element = ctk.CTkSwitch(master, text=text,
                                 variable=mainmenu_switch_var, onvalue=onvalue, offvalue=offvalue,
                                 font=("Arial", 10), text_color="white", progress_color="#7c6548")

def mainmenu_optionmenu(master, width=140, height=28, initvalue="", dynamic_resizing=False):
    mainmenu_optionmenu_var = ctk.StringVar(value=initvalue)
    return ctk.CTkOptionMenu(master, width=width, height=height, variable=mainmenu_optionmenu_var, dynamic_resizing=dynamic_resizing,
                                font=("Arial", 10), text_color="white", fg_color="#515151", button_color="#544430", 
                                dropdown_fg_color="#515151", button_hover_color="#b08c5f")

class mainmenu_selectbutton():
    def __init__(self, master, initvalue, values) -> None:
        mainmenu_selectbutton_var = ctk.StringVar(value=initvalue)
        self.element = ctk.CTkSegmentedButton(master, values=values, variable=mainmenu_selectbutton_var, fg_color="#515151", 
                                              selected_color="#7c6548", selected_hover_color="#b08c5f")

def mainmenu_buttoncanvas(master, width, height):
    """
    Scrollable canvas that contains buttons.\n
    By Razorwings18
    """
    return rwctk.rwCTk_ButtonCanvas(master, width=width, height=height, fg_color="#515151", border_width=1, border_color="#4d4d4d")

def mainmenu_checkbox(master, width=0, height=0, text="", checked=True):
    tempCheckbox = ctk.CTkCheckBox(master, width=width, height=height, text=text,
                                 font=("Arial", 10), text_color="white")
    if (checked):
        tempCheckbox.select()
    else:
        tempCheckbox.deselect()
    
    return tempCheckbox
###########################################################

######################## CENTER TAB ########################
def centertab_subframe(master):
    return ctk.CTkFrame(master, height=0, width=0, fg_color="#15120f", border_width=0)

def centertab_button(master, height=0, width=0, text="", image=None, border_width=0, corner_radius=0, command=None):
    return ctk.CTkButton(master, height=height, width=width, text=text, image=image, corner_radius=corner_radius,
                                         font=("Arial", 10), border_width=border_width, command=command, fg_color="#15120f", hover_color="#2a211a")

####################### DIALOG WINDOW ######################
def dialog_frame(master, width=0, height=0):
    return ctk.CTkFrame(master, height=height, width=width, fg_color="#353535", border_width=0)

def dialog_selectbutton(master, initvalue, values):
    dialog_selectbutton_var = ctk.StringVar(value=initvalue)
    return ctk.CTkSegmentedButton(master, values=values, variable=dialog_selectbutton_var, fg_color="#515151",
                                selected_color="#7c6548", selected_hover_color="#b08c5f")

def dialog_tabview(master, width=0, initvalue="", values=[], command=None):
    tabview = ctk.CTkTabview(master, width=width, fg_color="#515151", segmented_button_selected_color="#7c6548",
                        segmented_button_selected_hover_color="#b08c5f", command=command)

    """
    frameDict = {}
    for item in values:
        frameDict[item] = tabview.add(item)
    """
    for item in values:
        tabview.add(item)
    tabview.set(initvalue)

    #return frameDict, tabview
    return tabview

def dialog_submenu_tabview(master, width=0, initvalue="", values=[], command=None):
    tabview = ctk.CTkTabview(master, width=width, fg_color="#313131", segmented_button_selected_color="#5c4528",
                        segmented_button_selected_hover_color="#906c3f", command=command)
    for item in values:
        tabview.add(item)
    tabview.set(initvalue)
    return tabview

def dialog_submenu_frame(master, colormode:Literal["light", "dark"] = "light", border_width=0, corner_radius=0):
    if colormode=="dark":
        color = "#353535"
    elif colormode=="light":
        color = "#454545"
    return ctk.CTkFrame(master, height=0, width=0, fg_color=color, border_width=border_width, corner_radius=corner_radius)

def dialog_submenu_scrollable_frame(master, width, height, colormode:Literal["light", "dark"] = "light", border_width=0, corner_radius=0):
    if colormode=="dark":
        color = "#353535"
    elif colormode=="light":
        color = "#454545"
    return ctk.CTkScrollableFrame(master, height=height, width=width, fg_color=color, border_width=border_width, corner_radius=corner_radius)

def dialog_submenu_label(master, text):
    return ctk.CTkLabel(master, text=text, font=("Arial", 10), text_color="white")

def dialog_submenu_button(master, height=0, width=0, text="", image=None, border_width=0, corner_radius=0, command=None):
    return ctk.CTkButton(master, height=height, width=width, text=text, image=image, corner_radius=corner_radius,
                                         font=("Arial", 10), border_width=border_width, command=command, fg_color="#7c6548", hover_color="#b08c5f")

def dialog_largesubmenu_button(master, height=0, width=0, text="", image=None, border_width=0, corner_radius=0, command=None):
    return ctk.CTkButton(master, height=height, width=width, text=text, image=image, corner_radius=corner_radius,
                                         font=("Arial", 14), border_width=border_width, command=command, fg_color="#7c6548", hover_color="#b08c5f")

def dialog_listbox(master, width=0, height=0, command_on_click=None):
    listbox = tk.Listbox(master, width=width, height=height, background="#808080", highlightthickness=0, activestyle="none",
                         exportselection=0, selectmode=tk.SINGLE)
    if command_on_click != None:
        listbox.bind("<<ListboxSelect>>", command_on_click)
    return listbox

def dialog_checkbox(master, text, onvalue="on", offvalue="off", command=None, start_checked=False):
    check = ctk.CTkCheckBox(master, text=text, command=command, onvalue=onvalue, offvalue=offvalue,
                            font=("Arial", 10), fg_color="#7c6548")
    if start_checked:
        check.select()
    else:
        check.deselect()
    return check

class dialog_entry():
    def __init__(self, master, width, placeholder_text = "", starting_text = "", disallowed_chars = "", allowed_chars = "") -> None:
        self.element = ctk.CTkEntry(master, width=width, font=("Arial", 10), placeholder_text=placeholder_text,
                                   text_color="white", fg_color="#515151", height=15)
        
        if (disallowed_chars != "") or (allowed_chars != ""):
            self.disallowed_chars = disallowed_chars
            self.allowed_chars = allowed_chars
            self.element.bind("<Key>", self.validate_input) # validate="key" is not working on CTkEntry, so we'll do it manually
        self.element.bind("Tab", self.tab_handler)
        
        if len(starting_text)>0:
            self.element.insert(0, starting_text)
    
    def tab_handler(self, event):
        if event.state & 1:
            # Shift-Tab pressed. Shift-Tab doesn't do anything in the Entry, so we'll just let it slide.
            return
        else:
            # Tab pressed. Tab does add a Tab in the Entry, so we'll force the re-focus and prevent Tab from taking effect here.
            event.widget.tk_focusNext().focus()
        return "break"
    
    def validate_input(self, event):
        if event.keysym == 'BackSpace' or event.keysym == 'Tab':
            return
    
        # Now we'll check whether adding the character event.char results in a disallowed or in an allowed regular expression
        if (event.char) != "":
            char_entry_allowed = True
            
            if (self.disallowed_chars != ""):
                char_entry_allowed = re.match(self.disallowed_chars, self.element.get() + event.char) == None
            
            if (self.allowed_chars != "") and (char_entry_allowed):
                char_entry_allowed = re.match(self.allowed_chars, self.element.get() + event.char) != None
            
            if (not char_entry_allowed):
                return "break"