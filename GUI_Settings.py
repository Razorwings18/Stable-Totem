import customtkinter as ctk 
import tkinter as tk
from tkinter import filedialog
import GUIstyles as gs
import rwDialog
from PIL import Image
from typing import Literal
import common_functions
from tkinter import messagebox
import GUI_TTI_menu

class GUI_Settings():
    def __init__(self, TotemGUI) -> None:
        self._TotemGUI = TotemGUI
        TotemLang = self._TotemGUI._TotemLang
        self._TTImodels_path = self._TotemGUI.TTImodels_path
        
        self.dialog_window = None
        
        self._mainmenu_options = [TotemLang.LangString("GUI_Settings.mainmenu_model"),
                                    TotemLang.LangString("GUI_Settings.mainmenu_interface")]
        self._mainmenu_tabview = None

        # Submenu general globals
        self._something_changed: Literal["model.tti"] = "" # Did the user change any setting? Used to ask whether to apply changes if user tries to leave submenu
        
        # Models->TTI globals
        self._models_tti_mode:Literal["new", "edit"] = "" # Current mode (creating new model preset or editing an existing one?)
        self._TTI_models_list = None # The left panel list of models
        self._subframe_rightside_name_entry = None
        self._models_tti_widget = {}

    def DisplaySettingsGUI(self):
        self._BuildGUI()

    def _BuildGUI(self):
        TotemGUI = self._TotemGUI
        
        dialog_window_object = tk.Toplevel()
        dialog_window_object.title(TotemGUI._TotemLang.LangString("GUI_Settings.GeneralTitle"))
        dialog_window_object.resizable(False, False)  # Disable window resizing
        dialog_window_object.grab_set()  # Make the window modal
        self.dialog_window = dialog_window_object

        dialog_window_object.update_idletasks()  # Ensure dialog window is fully updated

        
        general_frame_width = TotemGUI._GetScaledPixelSize(TotemGUI._GetFullHDActualPixelWidthEquivalent(900))
        
        # Add the header menu
        self._BuildHeader(general_frame_width)

        # Build the sub-menus
        self._BuildSubmenus(general_frame_width)

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
    
    def _BuildHeader(self, general_frame_width):
        """
        Builds the header menu
        """
        TotemGUI = self._TotemGUI
        dialog_window = self.dialog_window

        # Create the frame that will contain the header menu. Since the header menu is a tabview, it will contain everything inside
        # the window as well.
        header_menu_frame = gs.dialog_frame(dialog_window, width=general_frame_width)

        # Create the header menu's tabview using the options stored in self._mainmenu_options
        mainmenu_tabview = gs.dialog_tabview(header_menu_frame, width=general_frame_width, initvalue=self._mainmenu_options[0],
                                                 values=self._mainmenu_options, command=self._mainmenu_tabview_click)
        self._mainmenu_tabview = mainmenu_tabview
        mainmenu_tabview.pack()
        
        header_menu_frame.pack()

        bottom_menu_frame = gs.dialog_frame(dialog_window)
        bottom_menu_frame_closebutton = gs.dialog_largesubmenu_button(bottom_menu_frame, text=self._TotemGUI._TotemLang.LangString("General.Close"),
                                                                      command=self._CloseSettings)
        bottom_menu_frame_closebutton.pack(side="right", anchor=tk.E, pady=5, padx=5)
        bottom_menu_frame.pack(expand="True", fill=tk.X)

    def _BuildSubmenus(self, general_frame_width):
        """
        Builds the frames for all the submenus
        """
        #TotemLang = self._TotemGUI._TotemLang

        #if (self._mainmenu_tabview.get() == TotemLang.LangString("GUI_Settings.mainmenu_model")):
        self._BuildModelSubmenu(general_frame_width)

    def _BuildModelSubmenu(self, general_frame_width):
        """
        Builds the Model submenu
        """
        TotemGUI = self._TotemGUI
        TotemLang = self._TotemGUI._TotemLang

        # Bring the Model main menu frame locally for ease of use
        frame = self._mainmenu_tabview.tab(TotemLang.LangString("GUI_Settings.mainmenu_model"))

        # These are all the model options that will be added to the tabview submenu
        model_submenu_options = [TotemLang.LangString("GUI_Settings.model.tti"), "Other"]
        
        # Create tabview with all the model options (tti, iti, upscale, etc.)
        model_submenu_tabview = gs.dialog_submenu_tabview(frame, width=general_frame_width, initvalue=model_submenu_options[0], 
                                                          values=model_submenu_options, command=self._model_submenu_tabview_click)
        
        # Build the Model->TTI submenu
        subframe = model_submenu_tabview.tab(TotemLang.LangString("GUI_Settings.model.tti"))
        
        ################################### Left frame #############################################
        subframe_leftside = gs.dialog_submenu_frame(subframe, colormode="light")
        
        # Buttons frame
        subframe_leftside_topbuttons = gs.dialog_submenu_frame(subframe_leftside, colormode="light")

        presetFileLabel = gs.dialog_submenu_label(subframe_leftside_topbuttons, text=TotemLang.LangString("GUI_Settings.model.tti.modelpresets"))
        presetFileLabel.pack(side="left", padx=2)

        presetDeleteButtonImage = ctk.CTkImage(Image.open(f"{TotemGUI._skin_path}\\deleteIcon.png"))
        presetDeleteButton = gs.dialog_submenu_button(subframe_leftside_topbuttons, height=0, width=0, text="", image=presetDeleteButtonImage, corner_radius=3,
                                            command=self._TTI_models_delete)
        presetDeleteButton.pack(side="right", padx=1)

        presetNewButtonImage = ctk.CTkImage(Image.open(f"{TotemGUI._skin_path}\\newfileIcon.png"))
        presetNewButton = gs.dialog_submenu_button(subframe_leftside_topbuttons, height=0, width=0, text="", image=presetNewButtonImage, corner_radius=3,
                                        command=self._model_tti_newPreset)
        presetNewButton.pack(side="right", padx=6)

        subframe_leftside_topbuttons.pack(fill=tk.X, expand=True, pady=4)

        # TTI Models list frame
        subframe_leftside_list = gs.dialog_submenu_frame(subframe_leftside, colormode="light")
        TTI_models_list = gs.dialog_listbox(subframe_leftside_list, width=30, height=15, command_on_click=self._TTI_models_clicked)
        TTI_models_list.pack()
        subframe_leftside_list.pack()

        subframe_leftside.grid(row=0, column=0)
        
        ########################################### Right frame ##############################################
        
        subframe_rightside = gs.dialog_submenu_frame(subframe, colormode="dark")
        self._subframe_model_tti_rightside = subframe_rightside
        
        subframe_rightside_scrollable = gs.dialog_submenu_scrollable_frame(subframe_rightside, width=TotemGUI._GetScaledPixelSize(TotemGUI._GetFullHDActualPixelWidthEquivalent(600)), 
                                                               height=TotemGUI._GetScaledPixelSize(TotemGUI._GetFullHDActualPixelWidthEquivalent(300)),
                                                               colormode="dark")
        
        ## General options
        subframe_rightside_general = gs.dialog_submenu_frame(subframe_rightside_scrollable, colormode="dark", border_width=1)
        
        #### General options intro frame
        subframe_rightside_general_topframe = gs.dialog_submenu_frame(subframe_rightside_general, colormode="dark")
        
        subframe_rightside_general_label = gs.dialog_submenu_label(subframe_rightside_general_topframe, TotemLang.LangString("GUI_Settings.model.tti.general_intro"))
        subframe_rightside_general_label.pack(anchor=tk.SW, padx=2, pady=1)

        subframe_rightside_general_topframe.pack()

        #### General options name frame
        subframe_rightside_general_nameframe = gs.dialog_submenu_frame(subframe_rightside_general, colormode="dark")
        
        subframe_rightside_name_label = gs.dialog_submenu_label(subframe_rightside_general_nameframe, TotemLang.LangString("GUI_Settings.model.tti.name_label"))
        subframe_rightside_name_label.pack(side=tk.LEFT, padx=5, pady=5)
        
        subframe_rightside_name_entry = gs.dialog_entry(subframe_rightside_general_nameframe, width=TotemGUI._GetScaledPixelSize(TotemGUI._GetFullHDActualPixelWidthEquivalent(200)), 
                                                        placeholder_text=TotemLang.LangString("GUI_Settings.model.tti.name_placeholder"),
                                                        disallowed_chars="")
        subframe_rightside_name_entry.element.pack(side=tk.LEFT, padx=5, pady=5)
        
        subframe_rightside_general_nameframe.pack(anchor=tk.NW, padx=1)
        
        #### General options bottom frame
        subframe_rightside_general_optionframe = gs.dialog_submenu_frame(subframe_rightside_general, colormode="dark")

        subframe_rightside_general_optionframe_isSDXL = gs.dialog_checkbox(subframe_rightside_general_optionframe,
                                                                    text=TotemLang.LangString("GUI_Settings.model.tti.general_isSDXL"))
        subframe_rightside_general_optionframe_isSDXL.pack(side=tk.BOTTOM, anchor=tk.W, padx=10, pady=4)

        subframe_rightside_general_optionframe.pack(anchor=tk.NW, padx=1)

        
        subframe_rightside_general.pack(padx=5, pady=5, ipadx=3, ipady=4, expand=True, fill=tk.X)
        
        ## UNET
        subframe_rightside_unet = gs.dialog_submenu_frame(subframe_rightside_scrollable, colormode="dark", border_width=1)
        
        #### UNET BROWSE FRAME
        subframe_rightside_unet_topframe = gs.dialog_submenu_frame(subframe_rightside_unet, colormode="dark")
        
        subframe_rightside_mainmodel_label = gs.dialog_submenu_label(subframe_rightside_unet_topframe, TotemLang.LangString("GUI_Settings.model.tti.mainmodel"))
        subframe_rightside_mainmodel_label.pack(anchor=tk.SW, padx=2, pady=1)

        subframe_rightside_mainmodel_entry = gs.dialog_entry(subframe_rightside_unet_topframe, width=TotemGUI._GetScaledPixelSize(TotemGUI._GetFullHDActualPixelWidthEquivalent(500)), 
                                                        placeholder_text=TotemLang.LangString("GUI_Settings.model.tti.mainmodel_placeholder"),
                                                        disallowed_chars="")
        subframe_rightside_mainmodel_entry.element.pack(side="left")
        
        subframe_rightside_mainmodel_browseimage = ctk.CTkImage(Image.open(f"{TotemGUI._skin_path}\\openIcon.png"))
        subframe_rightside_mainmodel_browse = gs.dialog_submenu_button(subframe_rightside_unet_topframe, height=0, width=0, text="", image=subframe_rightside_mainmodel_browseimage, corner_radius=3,
                                            command=lambda:rwDialog.SelectFolder(subframe_rightside_mainmodel_entry.element))
        subframe_rightside_mainmodel_browse.pack(side="right", padx=1)

        subframe_rightside_unet_topframe.pack()

        #### UNET OPTIMIZATIONS FRAME
        subframe_rightside_unet_optimizationframe = gs.dialog_submenu_frame(subframe_rightside_unet, colormode="dark")
        
        subframe_rightside_unet_optimizationframe_label = gs.dialog_submenu_label(subframe_rightside_unet_optimizationframe, TotemLang.LangString("GUI_Settings.model.tti.unet_optimization_label"))
        subframe_rightside_unet_optimizationframe_label.grid(row=0, column=0, columnspan=3, sticky=tk.SW, padx=2, pady=1)
        
        ###### Row 1
        subframe_rightside_unet_optimizationframe_fp16 = gs.dialog_checkbox(subframe_rightside_unet_optimizationframe,
                                                                    text=TotemLang.LangString("GUI_Settings.model.tti.optimization_fp16"))
        subframe_rightside_unet_optimizationframe_fp16.grid(row=1, column=0, columnspan=2, sticky=tk.W, padx=10, pady=4)

        subframe_rightside_unet_optimizationframe_safetensors = gs.dialog_checkbox(subframe_rightside_unet_optimizationframe,
                                                                    text=TotemLang.LangString("GUI_Settings.model.tti.optimization_safetensors"))
        subframe_rightside_unet_optimizationframe_safetensors.grid(row=1, column=2, sticky=tk.W, padx=10, pady=4)

        ###### Row 2
        subframe_rightside_unet_optimizationframe_torchcompile = gs.dialog_checkbox(subframe_rightside_unet_optimizationframe,
                                                                    text=TotemLang.LangString("GUI_Settings.model.tti.optimization_torchcompile"))
        subframe_rightside_unet_optimizationframe_torchcompile.grid(row=2, column=0, sticky=tk.W, padx=10, pady=4)

        subframe_rightside_unet_optimizationframe_vaetiling = gs.dialog_checkbox(subframe_rightside_unet_optimizationframe,
                                                                    text=TotemLang.LangString("GUI_Settings.model.tti.optimization_vaetiling"))
        subframe_rightside_unet_optimizationframe_vaetiling.grid(row=2, column=1, sticky=tk.W, padx=10, pady=4)

        subframe_rightside_unet_optimizationframe_xformers = gs.dialog_checkbox(subframe_rightside_unet_optimizationframe,
                                                                    text=TotemLang.LangString("GUI_Settings.model.tti.optimization_xformers"))
        subframe_rightside_unet_optimizationframe_xformers.grid(row=2, column=2, sticky=tk.W, padx=10, pady=4)

        ###### Row 3
        subframe_rightside_unet_optimizationframe_seqCPUoffload = gs.dialog_checkbox(subframe_rightside_unet_optimizationframe,
                                                                    text=TotemLang.LangString("GUI_Settings.model.tti.optimization_seqCPUoffload"))
        subframe_rightside_unet_optimizationframe_seqCPUoffload.grid(row=3, column=0, sticky=tk.W, padx=10, pady=4)

        subframe_rightside_unet_optimizationframe_modCPUoffload = gs.dialog_checkbox(subframe_rightside_unet_optimizationframe,
                                                                    text=TotemLang.LangString("GUI_Settings.model.tti.optimization_modCPUoffload"))
        subframe_rightside_unet_optimizationframe_modCPUoffload.grid(row=3, column=1, sticky=tk.W, padx=10, pady=4)

        subframe_rightside_unet_optimizationframe_attention = gs.dialog_checkbox(subframe_rightside_unet_optimizationframe,
                                                                    text=TotemLang.LangString("GUI_Settings.model.tti.optimization_attention"))
        subframe_rightside_unet_optimizationframe_attention.grid(row=3, column=2, sticky=tk.W, padx=10, pady=4)

        subframe_rightside_unet_optimizationframe.pack(anchor=tk.NW, padx=1)


        subframe_rightside_unet.pack(padx=5, pady=5, ipadx=3, ipady=4, expand=True, fill=tk.X)

        ## VAE
        subframe_rightside_vae = gs.dialog_submenu_frame(subframe_rightside_scrollable, colormode="dark", border_width=1)
        
        #### VAE BROWSE FRAME
        subframe_rightside_vae_topframe = gs.dialog_submenu_frame(subframe_rightside_vae, colormode="dark")
        
        subframe_rightside_vae_label = gs.dialog_submenu_label(subframe_rightside_vae_topframe, TotemLang.LangString("GUI_Settings.model.tti.vaemodel"))
        subframe_rightside_vae_label.pack(anchor=tk.SW, padx=2, pady=1)

        subframe_rightside_vae_entry = gs.dialog_entry(subframe_rightside_vae_topframe, width=TotemGUI._GetScaledPixelSize(TotemGUI._GetFullHDActualPixelWidthEquivalent(500)), 
                                                        placeholder_text=TotemLang.LangString("GUI_Settings.model.tti.vaemodel_placeholder"),
                                                        disallowed_chars="")
        subframe_rightside_vae_entry.element.pack(side="left")
        
        subframe_rightside_vae_browseimage = ctk.CTkImage(Image.open(f"{TotemGUI._skin_path}\\openIcon.png"))
        subframe_rightside_vae_browse = gs.dialog_submenu_button(subframe_rightside_vae_topframe, height=0, width=0, text="", image=subframe_rightside_vae_browseimage, corner_radius=3,
                                            command=lambda:rwDialog.SelectFolder(subframe_rightside_vae_entry.element))
        subframe_rightside_vae_browse.pack(side="right", padx=1)

        subframe_rightside_vae_topframe.pack()

        #### VAE OPTIONS
        subframe_rightside_vae_optionframe = gs.dialog_submenu_frame(subframe_rightside_vae, colormode="dark")
        
        subframe_rightside_vae_optionframe_usevae = gs.dialog_checkbox(subframe_rightside_vae_optionframe,
                                                                    text=TotemLang.LangString("GUI_Settings.model.tti.vaemodel_usevae"))
        subframe_rightside_vae_optionframe_usevae.pack(anchor=tk.W, padx=10, pady=4)

        subframe_rightside_vae_optionframe.pack(anchor=tk.NW, padx=1)

        
        subframe_rightside_vae.pack(padx=5, pady=5, ipadx=3, ipady=4, expand=True, fill=tk.X)

        ## REFINER
        subframe_rightside_refiner = gs.dialog_submenu_frame(subframe_rightside_scrollable, colormode="dark", border_width=1)
        
        #### REFINER BROWSE FRAME
        subframe_rightside_refiner_topframe = gs.dialog_submenu_frame(subframe_rightside_refiner, colormode="dark")
        
        subframe_rightside_refiner_label = gs.dialog_submenu_label(subframe_rightside_refiner_topframe, TotemLang.LangString("GUI_Settings.model.tti.refinermodel"))
        subframe_rightside_refiner_label.pack(anchor=tk.SW, padx=2, pady=1)

        subframe_rightside_refiner_entry = gs.dialog_entry(subframe_rightside_refiner_topframe, width=TotemGUI._GetScaledPixelSize(TotemGUI._GetFullHDActualPixelWidthEquivalent(500)), 
                                                        placeholder_text=TotemLang.LangString("GUI_Settings.model.tti.refinermodel_placeholder"),
                                                        disallowed_chars="")
        subframe_rightside_refiner_entry.element.pack(side="left")
        
        subframe_rightside_refiner_browseimage = ctk.CTkImage(Image.open(f"{TotemGUI._skin_path}\\openIcon.png"))
        subframe_rightside_refiner_browse = gs.dialog_submenu_button(subframe_rightside_refiner_topframe, height=0, width=0, text="", image=subframe_rightside_refiner_browseimage, corner_radius=3,
                                            command=lambda:rwDialog.SelectFolder(subframe_rightside_refiner_entry.element))
        subframe_rightside_refiner_browse.pack(side="right", padx=1)

        subframe_rightside_refiner_topframe.pack()
        
        #### REFINER GENERAL OPTIONS FRAME
        subframe_rightside_refiner_generalframe = gs.dialog_submenu_frame(subframe_rightside_refiner, colormode="dark")
        
        subframe_rightside_refiner_userefiner = gs.dialog_checkbox(subframe_rightside_refiner_generalframe,
                                                                    text=TotemLang.LangString("GUI_Settings.model.tti.refinermodel_userefiner"))
        subframe_rightside_refiner_userefiner.pack(anchor=tk.W, padx=10, pady=4)

        subframe_rightside_refiner_generalframe.pack(padx=3, expand=True, fill=tk.X)

        #### REFINER OPTIMIZATIONS FRAME
        subframe_rightside_refiner_optimizationframe = gs.dialog_submenu_frame(subframe_rightside_refiner, colormode="dark")
        
        subframe_rightside_refiner_optimizationframe_label = gs.dialog_submenu_label(subframe_rightside_refiner_optimizationframe, TotemLang.LangString("GUI_Settings.model.tti.refiner_optimization_label"))
        subframe_rightside_refiner_optimizationframe_label.grid(row=0, column=0, columnspan=3, sticky=tk.SW, padx=2, pady=1)
        
        ###### Row 1
        subframe_rightside_refiner_optimizationframe_fp16 = gs.dialog_checkbox(subframe_rightside_refiner_optimizationframe,
                                                                    text=TotemLang.LangString("GUI_Settings.model.tti.optimization_fp16"))
        subframe_rightside_refiner_optimizationframe_fp16.grid(row=1, column=0, columnspan=3, sticky=tk.W, padx=10, pady=4)

        subframe_rightside_refiner_optimizationframe_safetensors = gs.dialog_checkbox(subframe_rightside_refiner_optimizationframe,
                                                                    text=TotemLang.LangString("GUI_Settings.model.tti.optimization_safetensors"))
        subframe_rightside_refiner_optimizationframe_safetensors.grid(row=1, column=2, sticky=tk.W, padx=10, pady=4)

        ###### Row 2
        subframe_rightside_refiner_optimizationframe_torchcompile = gs.dialog_checkbox(subframe_rightside_refiner_optimizationframe,
                                                                    text=TotemLang.LangString("GUI_Settings.model.tti.optimization_torchcompile"))
        subframe_rightside_refiner_optimizationframe_torchcompile.grid(row=2, column=0, sticky=tk.W, padx=10, pady=4)

        subframe_rightside_refiner_optimizationframe_vaetiling = gs.dialog_checkbox(subframe_rightside_refiner_optimizationframe,
                                                                    text=TotemLang.LangString("GUI_Settings.model.tti.optimization_vaetiling"))
        subframe_rightside_refiner_optimizationframe_vaetiling.grid(row=2, column=1, sticky=tk.W, padx=10, pady=4)

        subframe_rightside_refiner_optimizationframe_xformers = gs.dialog_checkbox(subframe_rightside_refiner_optimizationframe,
                                                                    text=TotemLang.LangString("GUI_Settings.model.tti.optimization_xformers"))
        subframe_rightside_refiner_optimizationframe_xformers.grid(row=2, column=2, sticky=tk.W, padx=10, pady=4)

        ###### Row 3
        subframe_rightside_refiner_optimizationframe_seqCPUoffload = gs.dialog_checkbox(subframe_rightside_refiner_optimizationframe,
                                                                    text=TotemLang.LangString("GUI_Settings.model.tti.optimization_seqCPUoffload"))
        subframe_rightside_refiner_optimizationframe_seqCPUoffload.grid(row=3, column=0, sticky=tk.W, padx=10, pady=4)

        subframe_rightside_refiner_optimizationframe_modCPUoffload = gs.dialog_checkbox(subframe_rightside_refiner_optimizationframe,
                                                                    text=TotemLang.LangString("GUI_Settings.model.tti.optimization_modCPUoffload"))
        subframe_rightside_refiner_optimizationframe_modCPUoffload.grid(row=3, column=1, sticky=tk.W, padx=10, pady=4)

        subframe_rightside_refiner_optimizationframe_attention = gs.dialog_checkbox(subframe_rightside_refiner_optimizationframe,
                                                                    text=TotemLang.LangString("GUI_Settings.model.tti.optimization_attention"))
        subframe_rightside_refiner_optimizationframe_attention.grid(row=3, column=2, sticky=tk.W, padx=10, pady=4)

        subframe_rightside_refiner_optimizationframe.pack(anchor=tk.NW, padx=1)


        subframe_rightside_refiner.pack(padx=5, pady=5, ipadx=3, ipady=4, expand=True, fill=tk.X)

        ## VAE
        subframe_rightside_refinervae = gs.dialog_submenu_frame(subframe_rightside_scrollable, colormode="dark", border_width=1)
        
        #### VAE BROWSE FRAME
        subframe_rightside_refinervae_topframe = gs.dialog_submenu_frame(subframe_rightside_refinervae, colormode="dark")
        
        subframe_rightside_refinervae_label = gs.dialog_submenu_label(subframe_rightside_refinervae_topframe, TotemLang.LangString("GUI_Settings.model.tti.refinervaemodel"))
        subframe_rightside_refinervae_label.pack(anchor=tk.SW, padx=2, pady=1)

        subframe_rightside_refinervae_entry = gs.dialog_entry(subframe_rightside_refinervae_topframe, width=TotemGUI._GetScaledPixelSize(TotemGUI._GetFullHDActualPixelWidthEquivalent(500)), 
                                                        placeholder_text=TotemLang.LangString("GUI_Settings.model.tti.vaemodel_placeholder"),
                                                        disallowed_chars="")
        subframe_rightside_refinervae_entry.element.pack(side="left")
        
        subframe_rightside_refinervae_browseimage = ctk.CTkImage(Image.open(f"{TotemGUI._skin_path}\\openIcon.png"))
        subframe_rightside_refinervae_browse = gs.dialog_submenu_button(subframe_rightside_refinervae_topframe, height=0, width=0, text="", image=subframe_rightside_refinervae_browseimage, corner_radius=3,
                                            command=lambda:rwDialog.SelectFolder(subframe_rightside_refinervae_entry.element))
        subframe_rightside_refinervae_browse.pack(side="right", padx=1)

        subframe_rightside_refinervae_topframe.pack()

        #### VAE OPTIONS
        subframe_rightside_refinervae_optionframe = gs.dialog_submenu_frame(subframe_rightside_refinervae, colormode="dark")
        
        subframe_rightside_refinervae_optionframe_usevae = gs.dialog_checkbox(subframe_rightside_refinervae_optionframe,
                                                                    text=TotemLang.LangString("GUI_Settings.model.tti.refinervaemodel_usevae"))
        subframe_rightside_refinervae_optionframe_usevae.pack(anchor=tk.W, padx=10, pady=4)

        subframe_rightside_refinervae_optionframe.pack(anchor=tk.NW, padx=1)

        
        subframe_rightside_refinervae.pack(padx=5, pady=5, ipadx=3, ipady=4, expand=True, fill=tk.X)

        subframe_rightside_scrollable.pack()

        ## Non-scrolling bottom frame
        subframe_rightside_bottom = gs.dialog_submenu_frame(subframe_rightside, colormode="light", corner_radius=0)
        
        subframe_rightside_bottom_cancelbutton = gs.dialog_largesubmenu_button(subframe_rightside_bottom, text=TotemLang.LangString("General.Cancel"),
                                                                               command=self._models_tti_cancel)
        subframe_rightside_bottom_cancelbutton.pack(side="right", anchor=tk.E, pady=5, padx=5)
        subframe_rightside_bottom_applybutton = gs.dialog_largesubmenu_button(subframe_rightside_bottom, text=TotemLang.LangString("General.Apply"),
                                                                              command=self._models_tti_apply)
        subframe_rightside_bottom_applybutton.pack(side="right", anchor=tk.E, pady=5, padx=5)
        
        subframe_rightside_bottom.pack(expand=True, fill=tk.X)

        model_submenu_tabview.pack()

        subframe.update()
        frame.update()

        # Create globals for all widgets that will need to be accessed externally
        self._model_submenu_tabview = model_submenu_tabview
        self._TTI_models_list = TTI_models_list
        self._subframe_rightside_name_entry = subframe_rightside_name_entry.element
        ## The state of all the widgets below will be saved to (and retrieved from) the JSON. Don't add anything that shouldn't be saved in the JSON.
        self._models_tti_widget['subframe_rightside_general_optionframe_isSDXL'] = subframe_rightside_general_optionframe_isSDXL

        self._models_tti_widget['subframe_rightside_mainmodel_entry'] = subframe_rightside_mainmodel_entry.element
        self._models_tti_widget['subframe_rightside_unet_optimizationframe_fp16'] = subframe_rightside_unet_optimizationframe_fp16
        self._models_tti_widget['subframe_rightside_unet_optimizationframe_safetensors'] = subframe_rightside_unet_optimizationframe_safetensors
        self._models_tti_widget['subframe_rightside_unet_optimizationframe_torchcompile'] = subframe_rightside_unet_optimizationframe_torchcompile
        self._models_tti_widget['subframe_rightside_unet_optimizationframe_vaetiling'] = subframe_rightside_unet_optimizationframe_vaetiling
        self._models_tti_widget['subframe_rightside_unet_optimizationframe_xformers'] = subframe_rightside_unet_optimizationframe_xformers
        self._models_tti_widget['subframe_rightside_unet_optimizationframe_seqCPUoffload'] = subframe_rightside_unet_optimizationframe_seqCPUoffload
        self._models_tti_widget['subframe_rightside_unet_optimizationframe_modCPUoffload'] = subframe_rightside_unet_optimizationframe_modCPUoffload
        self._models_tti_widget['subframe_rightside_unet_optimizationframe_attention'] = subframe_rightside_unet_optimizationframe_attention

        self._models_tti_widget['subframe_rightside_vae_entry'] = subframe_rightside_vae_entry.element
        self._models_tti_widget['subframe_rightside_vae_optionframe_usevae'] = subframe_rightside_vae_optionframe_usevae

        self._models_tti_widget['subframe_rightside_refiner_entry'] = subframe_rightside_refiner_entry.element
        self._models_tti_widget['subframe_rightside_refiner_userefiner'] = subframe_rightside_refiner_userefiner
        self._models_tti_widget['subframe_rightside_refiner_optimizationframe_fp16'] = subframe_rightside_refiner_optimizationframe_fp16
        self._models_tti_widget['subframe_rightside_refiner_optimizationframe_safetensors'] = subframe_rightside_refiner_optimizationframe_safetensors
        self._models_tti_widget['subframe_rightside_refiner_optimizationframe_torchcompile'] = subframe_rightside_refiner_optimizationframe_torchcompile
        self._models_tti_widget['subframe_rightside_refiner_optimizationframe_vaetiling'] = subframe_rightside_refiner_optimizationframe_vaetiling
        self._models_tti_widget['subframe_rightside_refiner_optimizationframe_xformers'] = subframe_rightside_refiner_optimizationframe_xformers
        self._models_tti_widget['subframe_rightside_refiner_optimizationframe_seqCPUoffload'] = subframe_rightside_refiner_optimizationframe_seqCPUoffload
        self._models_tti_widget['subframe_rightside_refiner_optimizationframe_modCPUoffload'] = subframe_rightside_refiner_optimizationframe_modCPUoffload
        self._models_tti_widget['subframe_rightside_refiner_optimizationframe_attention'] = subframe_rightside_refiner_optimizationframe_attention

        self._models_tti_widget['subframe_rightside_refinervae_entry'] = subframe_rightside_refinervae_entry.element
        self._models_tti_widget['subframe_rightside_refinervae_optionframe_usevae'] = subframe_rightside_refinervae_optionframe_usevae

        # Bind a process to all fields, to get notified if something changes
        subframe_rightside_name_entry.element.bind("<KeyPress>", self._model_tti_widgetchanged)
        subframe_rightside_mainmodel_browse.bind("<Button-1>", self._model_tti_widgetchanged)
        subframe_rightside_vae_browse.bind("<Button-1>", self._model_tti_widgetchanged)
        subframe_rightside_refiner_browse.bind("<Button-1>", self._model_tti_widgetchanged)
        subframe_rightside_refinervae_browse.bind("<Button-1>", self._model_tti_widgetchanged)
        for i, widget in self._models_tti_widget.items():
            if isinstance(widget, ctk.CTkEntry):
                widget.bind("<KeyPress>", self._model_tti_widgetchanged)
            elif isinstance(widget, ctk.CTkCheckBox):
                widget.bind("<Button-1>", self._model_tti_widgetchanged)

        # Emulate a click on the submenu's tabview, so that the first selected section is initialized
        self._model_submenu_tabview_click()

    def _model_tti_widgetchanged(self, event):
        self._something_changed = "model.tti"

    def _model_tti_newPreset(self):
        TotemGUI = self._TotemGUI
        TotemLang = self._TotemGUI._TotemLang

        if self._CheckForChanges()=="goback.model.tti":
            return

        self._models_tti_mode = "new"
        self._TTI_models_list.insert(0, "<new model preset>")
        self._TTI_models_list.select_clear(0, tk.END)  # Clear any previous selections
        self._TTI_models_list.select_set(0) # Select the new preset in the list
        self._TTI_models_reset() # Reset all fields
        self._SubframeVisibility("subframe_model_tti_rightside", True) # Show the right side frame
        self._something_changed = "model.tti"
        
        self._TTI_models_list._last_selection = 0 # Since the listbox selection is done programatically, we force this to avoid future conflicts.

    def _models_tti_apply(self):
        """
        Applies (saves) all info in the Models -> TTI menu
        """
        TTImodels_path = self._TTImodels_path
        TotemLang = self._TotemGUI._TotemLang

        # Load the contents of the JSON into a dictionary
        existing_json = common_functions.load_json_from_file(TTImodels_path)

        new_model_name = self._subframe_rightside_name_entry.get().strip()
        if (len(new_model_name)>0):
            if (self._models_tti_mode == "new"):
                # We're adding a new model preset.
                # Verify that a model preset with the chosen name does not already exist.
                for item in self._TTI_models_list.get(1, tk.END):
                    if item.lower() == new_model_name.lower():
                        messagebox.showinfo(TotemLang.LangString("GUI_Settings.model.tti.newmodel_exists_title"),
                                            TotemLang.LangString("GUI_Settings.model.tti.newmodel_exists_content"))
                        return
                
                # Create a new "model" element to add to the JSON file with all current widget values.
                self._model_tti_addNewElementToJSONDictionary(existing_json, new_model_name)
                
                # Write the updated JSON data with the added model preset
                common_functions.save_json_to_file(TTImodels_path, existing_json)

                # Change the placeholder text in the listbox to the actual name
                self._TTI_models_list.delete(0)
                self._TTI_models_list.insert(0, new_model_name)
                
                # Once the new model preset is created, we are now actually editing it
                self._models_tti_mode = "edit"
            elif (self._models_tti_mode=="edit"):
                # Verify that a model preset with the chosen name does not already exist.
                for i, item in enumerate(self._TTI_models_list.get(0, tk.END)):
                    if item.lower() == new_model_name.lower():
                        if not (self._TTI_models_list.selection_includes(i)):
                            messagebox.showinfo(TotemLang.LangString("GUI_Settings.model.tti.newmodel_exists_title"),
                                                TotemLang.LangString("GUI_Settings.model.tti.newmodel_exists_content"))
                            return
                
                # Get the index of the selected model in existing_json
                selected_model_name = self._TTI_models_list.get(self._TTI_models_list.curselection()[0])
                for i, value in enumerate(existing_json['model']):
                    if (value['name']==selected_model_name):
                        selected_model_index = i
                        break
                # Now delete the selected model from existing_json
                del existing_json['model'][selected_model_index]

                # Add a new element to existing_json for the selected model, with all of its parameters
                self._model_tti_addNewElementToJSONDictionary(existing_json, new_model_name)

                # Finally, write the updated JSON data to the file
                common_functions.save_json_to_file(TTImodels_path, existing_json)

                # Update the model's name in the listbox
                old_selection_index = self._TTI_models_list.curselection()[0]
                self._TTI_models_list.delete(old_selection_index)
                self._TTI_models_list.insert(old_selection_index, new_model_name)

                # And remove the "something changed" mark
                self._something_changed = ""

                # And tell the user everything went OK
                messagebox.showinfo(TotemLang.LangString("GUI_Settings.model.tti.apply_successful_title"),
                                    TotemLang.LangString("GUI_Settings.model.tti.apply_successful_content", [selected_model_name]))
        else:
            messagebox.showinfo(TotemLang.LangString("GUI_Settings.model.tti.newmodel_emptyname_title"),
            TotemLang.LangString("GUI_Settings.model.tti.newmodel_emptyname_content"))

    def _models_tti_cancel(self):
        """
        Callable for when Cancel is pressed in Models -> TTI
        """
        if (self._models_tti_mode=="new"):
            self._something_changed = ""
            self._TTI_models_list.delete(0)
            self._SubframeVisibility("subframe_model_tti_rightside", False)
        elif (self._models_tti_mode=="edit"):
            self._something_changed = ""
            self._TTI_models_list.select_clear(0, tk.END)
            self._SubframeVisibility("subframe_model_tti_rightside", False)
        self._models_tti_mode = ""

    def _model_tti_addNewElementToJSONDictionary(self, existing_json, name):
        new_model = {}
        new_model['name'] = name
        
        for key, widget in self._models_tti_widget.items():
            keyname = key.replace("subframe_rightside_", "")
            if isinstance(widget, ctk.CTkEntry):
                value = widget.get()
            elif isinstance(widget, ctk.CTkCheckBox):
                value = widget.get() == "on"
            new_model[keyname] = value
        
        # Add the new element to the "model" dictionary value
        existing_json['model'].append(new_model)

    def _TTI_models_reset(self):
        """
        Resets all widgets in the Models -> TTI menu
        """
        self._subframe_rightside_name_entry.delete(0, tk.END)
        for key, widget in self._models_tti_widget.items():
            if isinstance(widget, ctk.CTkEntry):
                widget.delete(0, tk.END)
            elif isinstance(widget, ctk.CTkCheckBox):
                widget.deselect()

    def _SubframeVisibility(self, frame_name:Literal["subframe_model_tti_rightside"], set_to_visible:bool):
        """
        Shows / Hides the frames that correspond to frame_name
        """
        if (frame_name) == "subframe_model_tti_rightside":
            if set_to_visible:
                self._subframe_model_tti_rightside.grid(row=0, column=1, sticky=tk.NW)
            else:
                self._subframe_model_tti_rightside.grid_forget()

    def _mainmenu_tabview_click(self):
        if self._CheckForChanges()=="goback.model.tti":
            return

    def _model_submenu_tabview_click(self):
        if self._CheckForChanges()=="goback.model.tti":
            return
        
        if self._model_submenu_tabview.get() == self._TotemGUI._TotemLang.LangString("GUI_Settings.model.tti"):
            self._subframe_model_tti_rightside.grid_forget() # Hide right-side panel
            self._model_tti_populateList()

    def _model_tti_populateList(self):
        existing_json = common_functions.load_json_from_file(self._TTImodels_path)
        
        # Clear the list
        self._TTI_models_list.delete(0, tk.END)

        # Add the model names taken from the JSON
        for model in existing_json['model']:
            self._TTI_models_list.insert(tk.END, model['name'])

    def _TTI_models_delete(self):
        """
        Deletes selected TTI model preset
        """
        TotemLang = self._TotemGUI._TotemLang

        verification = rwDialog.RestrictiveInputDialog(TotemLang.LangString("General.Confirmation"), 
                                           TotemLang.LangString("GUI_Settings.model.tti.delete_messagebox", [TotemLang.LangString("General.ReplyYES")]), 
                                           "")()
        if verification == None:
            return
        
        if verification.lower() == TotemLang.LangString("General.ReplyYES").lower():
            TTImodels_path = self._TTImodels_path
            
            # Load the Models -> TTI JSON into a dictionary
            existing_json = common_functions.load_json_from_file(TTImodels_path)

            # Go through the existing_json elements until the one that corresponds to the selected model preset is found,
            # and delete it from existing_json
            model_name = self._TTI_models_list.get(self._TTI_models_list.curselection()[0]) # This is the selected model
            for i, widget_params in enumerate(existing_json['model']):
                if (widget_params['name']==model_name):
                    del existing_json['model'][i] # remove the model from existing_json
                    break
            
            # Save the Models -> TTI JSON without the deleted model preset
            common_functions.save_json_to_file(TTImodels_path, existing_json)

            self._something_changed = False

            self._TTI_models_reset() # Reset all fields
            self._SubframeVisibility("subframe_model_tti_rightside", False) # Hide the right side frame

            self._model_tti_populateList() # Repopulate the model list
    
    def _TTI_models_clicked(self, *kwargs):
        if self._CheckForChanges()=="goback.model.tti":
            # Reselect the item that was previously selected (corresponding to the model that is being edited)
            self._TTI_models_list.selection_clear(0, tk.END)
            if not hasattr(self._TTI_models_list, "_last_selection"):
                self._TTI_models_list._last_selection = 0
            self._TTI_models_list.selection_set(self._TTI_models_list._last_selection)

            return
        
        TTImodels_path = self._TTImodels_path
        
        # Load the Models -> TTI JSON into a dictionary
        existing_json = common_functions.load_json_from_file(TTImodels_path)

        self._models_tti_mode = "edit"
        self._TTI_models_reset() # Reset all fields
        self._SubframeVisibility("subframe_model_tti_rightside", True) # Show the right side frame

        # Go through the existing_json elements until the one that corresponds to the selected model preset is found, and load it in json_params
        model_name = self._TTI_models_list.get(self._TTI_models_list.curselection()[0])
        for widget_params in existing_json['model']:
            if (widget_params['name']==model_name):
                json_params = widget_params
                break

        widgets = self._models_tti_widget
        # Populate all fields
        self._subframe_rightside_name_entry.insert(0, model_name)

        for key, value in json_params.items():
            widgetname = "subframe_rightside_" + key

            if (widgetname in widgets):
                if isinstance(widgets[widgetname], ctk.CTkEntry):
                    widgets[widgetname].insert(0, value)
                elif isinstance(widgets[widgetname], ctk.CTkCheckBox):
                    if value:
                        widgets[widgetname].select()
                    else:
                        widgets[widgetname].deselect()
        
        # Save the currently-selected index for future reference
        self._TTI_models_list._last_selection = self._TTI_models_list.curselection()[0]

    def _CheckForChanges(self):
        TotemLang = self._TotemGUI._TotemLang
        
        if self._something_changed == "model.tti":
            result = rwDialog.MultiButtonDialog(TotemLang.LangString("GUI_Settings.model.tti.somethingchanged_title"),
                                       TotemLang.LangString("GUI_Settings.model.tti.somethingchanged_content"),
                                       [TotemLang.LangString("General.GoBack"), TotemLang.LangString("General.DiscardChanges")])()
            self.dialog_window.grab_set()  # Make the main window modal again, since calling the dialog above reverts modality
            
            if (result == TotemLang.LangString("General.GoBack")):
                self._mainmenu_tabview.set(TotemLang.LangString("GUI_Settings.mainmenu_model"))
                self._model_submenu_tabview.set(TotemLang.LangString("GUI_Settings.model.tti"))
                return "goback.model.tti"
            else:
                self._something_changed = ""

                if self._models_tti_mode=="new":
                    self._models_tti_cancel()
        return ""

    def _CloseSettings(self):
        if self._CheckForChanges()=="goback.model.tti":
            return
        
        # If the app is in TTI mode, update stuff that may have changed and affects it
        if self._TotemGUI._current_mode == "TTI":
            # Update the models preset list
            GUI_TTI_menu._FillTTIModelPresets(self._TotemGUI)
            # Reload the selected model (if any)
            GUI_TTI_menu._TTIModelPresetLoad(self._TotemGUI, self._TotemGUI._TTImodelmenu.get())
        
        self.dialog_window.destroy()