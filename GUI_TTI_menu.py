import tkinter as tk
import customtkinter as ctk 
from PIL import ImageTk, Image
import GUIstyles as gs
import promptPresetOperations as ppo
import common_functions as cf

global currentModelLabel

def _BuildTTIPromptMenu(TotemGUI_instance):
    """
    Builds the TTI left-side menu.\n
    There will be one frame with the attribute ".scrollable" that will be resizable when the main window is resized;
    all other frames will remain the same size.
    """
    # Since we can't import TotemGUI due to circular reference, make a "mini-cast" here
    from GUI import TotemGUI
    self:TotemGUI = TotemGUI_instance

    TotemLang = self._TotemLang # Bring the TotemLang instance locally
    global currentModelLabel

    # Load the JSON settings for TTI
    settings_json = cf.load_json_from_file(self.general_settings_file)

    def on_canvas_configure(event):
        canvas.configure(scrollregion=canvas.bbox("all"))

    def on_scrollbar_move(*args):
        canvas.yview(*args)

    def canvas_on_mousewheel(event):
        # Scroll the canvas vertically
        canvas.yview_scroll(-1 * (event.delta // 120), "units")

    def bind_children_recursive(widget, event, callback):
        try:
            widget.bind(event, callback)
        except:
            cf.LogEntry(title="Cannot bind mousewheel to TTI_main_frame child", message=f"Widget {widget} does not support MouseWheel binding", 
                        type="info", show_messagebox=False)
        for child in widget.winfo_children():
            bind_children_recursive(child, event, callback)

    def TTI_main_frame_final_actions():
        canvas.configure(width=TTI_main_frame.winfo_width())
        on_canvas_configure(None)

    left_menu_parent_frame = ctk.CTkFrame(self._app, width=0, height=0)
    self._left_menu_parent_frame = left_menu_parent_frame
    left_menu_parent_frame.place(x=0, y=self._GetScaledPixelSize(self._GetFullHDActualPixelWidthEquivalent(125)))
    
    scrollable_left_frame = ctk.CTkFrame(left_menu_parent_frame, width=0, height=0, fg_color="#1e1e1e")
    scrollable_left_frame.scrollable = True
    self._scrollable_left_menu_frame = scrollable_left_frame
    scrollable_left_frame.pack()

    canvas = tk.Canvas(scrollable_left_frame, bg="black", width=0, height=0, highlightthickness=0)
    self._left_menu_canvas = canvas
    canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    scrollbar = ctk.CTkScrollbar(scrollable_left_frame, orientation=tk.VERTICAL, command=on_scrollbar_move, fg_color="#1c130e", 
                                 button_color="#ddb27f", button_hover_color="#ba9a74")
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    TTI_main_frame = ctk.CTkFrame(canvas, fg_color="#1e1e1e")
    
    ############################### MODEL FRAME ####################################
    frameModel = gs.mainmenu_frame(TTI_main_frame)

    subframeModel2 = gs.mainmenu_subframe(frameModel, border_width=0)
    currentModelLabel = gs.mainmenu_inner_label(subframeModel2)
    currentModelLabel.element.pack(side="left", padx=2)
    subframeModel2.pack(ipady=2, ipadx=5, padx=2, fill="x")

    subframeModel1 = gs.mainmenu_subframe(frameModel)
    
    modelLabel = gs.mainmenu_inner_label(subframeModel1, text=TotemLang.LangString("GUI_TTI_menu.modelframe.modelpreset"))
    modelLabel.element.pack(side="left", padx=2)

    modelMenu = gs.mainmenu_optionmenu(subframeModel1, width=150, initvalue="")
    self._TTImodelmenu = modelMenu
    _FillTTIModelPresets(self)
    if "TTI_model_preset" in settings_json:
        if settings_json['TTI_model_preset'] in modelMenu.cget("values"):
            modelMenu.set(settings_json['TTI_model_preset'])
    modelMenu.pack(side="left", padx=2)

    modelLoadButtonImage = ctk.CTkImage(Image.open(f"{self._skin_path}\\openIcon.png"))
    modelLoadButton = gs.mainmenu_button(subframeModel1, height=0, width=0, text="", image=modelLoadButtonImage, corner_radius=3,
                                        command=lambda:_TTIModelPresetLoad(self, modelMenu.get()))
    modelLoadButton.pack(side="left", padx=1)
    
    subframeModel1.pack(ipady=2, ipadx=5, padx=2, fill="x")

    frameModel.pack(padx=2, pady=2, ipadx=3, ipady=3, anchor="w", fill="x")        
    
    ############################### TOP FRAME ######################################
    frameTop = gs.mainmenu_frame(TTI_main_frame)
    
    subframeTop1 = gs.mainmenu_subframe(frameTop)
    subframeTop1.configure(border_width=0)

    heightLabel = gs.mainmenu_inner_label(subframeTop1, text="Height")
    heightLabel.element.pack(side="left", padx=2)
    
    heightTextbox = gs.mainmenu_inner_entry(subframeTop1, width=50, placeholder_text="<def>", allowed_chars=r'^\d+$')
    heightTextbox.element.pack(side="left", padx=5)

    widthLabel = gs.mainmenu_inner_label(subframeTop1, text="Width")
    widthLabel.element.pack(side="left")

    widthTextbox = gs.mainmenu_inner_entry(subframeTop1, width=50, placeholder_text="<def>", allowed_chars=r'^\d+$')
    widthTextbox.element.pack(side="left", padx=5)

    imgnumberLabel = gs.mainmenu_inner_label(subframeTop1, text="# of images\nto generate")
    imgnumberLabel.element.pack(side="left")

    imgnumberSelector = gs.mainmenu_selectbutton(subframeTop1, values=["1", "2", "4"], initvalue="1")
    imgnumberSelector.element.pack(side="left", padx=5)
    
    subframeTop1.pack(ipady=5, ipadx=5, padx=2, fill="x")


    subframeTop2 = gs.mainmenu_subframe(frameTop)
    
    presetFileLabel = gs.mainmenu_inner_label(subframeTop2, text="Prompt Presets")
    presetFileLabel.element.pack(side="left", padx=2)

    self._presetFileMenu = gs.mainmenu_optionmenu(subframeTop2, width=110, initvalue="")
    ppo.PopulatePresetFilesList(preset_file_menu=self._presetFileMenu)
    self._presetFileMenu.pack(side="left", padx=2)

    presetLoadButtonImage = ctk.CTkImage(Image.open(f"{self._skin_path}\\openIcon.png"))
    presetLoadButton = gs.mainmenu_button(subframeTop2, height=0, width=0, text="", image=presetLoadButtonImage, corner_radius=3,
                                        command=lambda:ppo.PromptPresetLoad(self, self._presetFileMenu.get()))
    presetLoadButton.pack(side="left", padx=1)

    presetSaveButtonImage = ctk.CTkImage(Image.open(f"{self._skin_path}\\saveIcon.png"))
    presetSaveButton = gs.mainmenu_button(subframeTop2, height=0, width=0, text="", image=presetSaveButtonImage, corner_radius=3,
                                        command=lambda:ppo.PromptPresetSave(preset_prompt_buttons=self._preset_prompt_canvas.buttons, 
                                                                        negative_preset_prompt_buttons=self._preset_negative_prompt_canvas.buttons,
                                                                        selected_preset=self._presetFileMenu.get()))
    presetSaveButton.pack(side="left", padx=1)        
    
    presetDeleteButtonImage = ctk.CTkImage(Image.open(f"{self._skin_path}\\deleteIcon.png"))
    presetDeleteButton = gs.mainmenu_button(subframeTop2, height=0, width=0, text="", image=presetDeleteButtonImage, corner_radius=3,
                                        command=lambda:ppo.PromptDelete(self._presetFileMenu, self._presetFileMenu.get()))
    presetDeleteButton.pack(side="left", padx=1)

    presetNewButtonImage = ctk.CTkImage(Image.open(f"{self._skin_path}\\newfileIcon.png"))
    presetNewButton = gs.mainmenu_button(subframeTop2, height=0, width=0, text="", image=presetNewButtonImage, corner_radius=3,
                                    command=lambda:ppo.PromptPresetNew(preset_file_menu=self._presetFileMenu,
                                                                        preset_prompt_buttons=self._preset_prompt_canvas.buttons, 
                                                                        negative_preset_prompt_buttons=self._preset_negative_prompt_canvas.buttons,
                                                                        selected_preset=self._presetFileMenu.get()))
    presetNewButton.pack(side="left", padx=6)

    subframeTop2.pack(side="left", ipady=5, ipadx=5, padx=2, fill="x")

    frameTop.pack(padx=2, pady=2, ipadx=3, ipady=3, anchor="w", fill="x")
    ######################################################################
    
    ############################### PROMPT FRAME ######################################
    ### POSITIVE
    framePrompt = gs.mainmenu_frame(TTI_main_frame, fg_color="#1e1e1e")
    
    thisrow=0
    promptLabel = gs.mainmenu_inner_label(framePrompt, text="Prompt")
    promptLabel.element.grid(row=thisrow, columnspan=2, stick="w")

    thisrow+=1
    promptTexbox = gs.mainmenu_inner_textbox(framePrompt, width=325, height=80)
    self._TTIpromptTextbox = promptTexbox.element
    promptTexbox.element.configure(font=("Arial", 12))
    promptTexbox.element.grid(row=thisrow, columnspan=2, stick="w")
    promptTexbox.element.bind("<KeyPress>", self._preventCRTAB_Entry)

    thisrow+=1
    presetPromptLabel = gs.mainmenu_inner_label(framePrompt, text="Preset prompts")
    presetPromptLabel.element.grid(row=thisrow, column=0, stick="w")
    
    presetPromptClearImage = ctk.CTkImage(Image.open(f"{self._skin_path}\\clear.png"), size=(16, 16))
    presetPromptClear = gs.mainmenu_button_contour(framePrompt, height=0, width=0, text="", image=presetPromptClearImage, 
                                        command=lambda:ppo.ClearPresets(self._preset_prompt_canvas))
    presetPromptClear.element.grid(row=thisrow, column=1, stick="e")
    
    thisrow+=1
    _dummyFrame = ctk.CTkFrame(framePrompt)
    self._preset_prompt_canvas = gs.mainmenu_buttoncanvas(_dummyFrame, width=305, height=50)
    _dummyFrame.grid(row=thisrow, columnspan=2, stick="w")

    thisrow+=1
    presetPromptText = gs.mainmenu_inner_entry(framePrompt, width=280, placeholder_text="<Add preset prompt...>")
    presetPromptText.element.bind("<Return>", lambda event: ppo.AddPresetPromptFromGUI(self, presetPromptText.element, 
                                                                                    self._preset_prompt_canvas, "positive"))
    presetPromptText.element.grid(row=thisrow, column=0, stick="w", pady=5)
    
    presetPromptButton = gs.mainmenu_button(framePrompt, height=10, width=40, text="Add", 
                                        command=lambda: ppo.AddPresetPromptFromGUI(self, presetPromptText.element,
                                                                                self._preset_prompt_canvas, "positive"))
    presetPromptButton.grid(row=thisrow, column=1, stick="e")

    framePrompt.pack(padx=2, pady=2, ipadx=3, ipady=3, anchor="w")


    ### NEGATIVE
    frameNegativePrompt = gs.mainmenu_frame(TTI_main_frame)
    
    thisrow=0
    negative_promptLabel = gs.mainmenu_inner_label(frameNegativePrompt, text="Negative Prompt")
    negative_promptLabel.element.grid(row=thisrow, columnspan=2, stick="w")

    thisrow+=1
    negative_promptTexbox = gs.mainmenu_inner_textbox(frameNegativePrompt, width=325, height=50)
    self._TTInegative_promptTextbox = negative_promptTexbox.element
    negative_promptTexbox.element.configure(font=("Arial", 12))
    negative_promptTexbox.element.grid(row=thisrow, columnspan=2, stick="w")
    negative_promptTexbox.element.bind("<KeyPress>", self._preventCRTAB_Entry)

    thisrow+=1
    presetNegativePromptLabel = gs.mainmenu_inner_label(frameNegativePrompt, text="Preset negative prompts")
    presetNegativePromptLabel.element.grid(row=thisrow, column=0, stick="w")
    
    presetNegativePromptClearImage = ctk.CTkImage(Image.open(f"{self._skin_path}\\clear.png"), size=(16, 16))
    presetNegativePromptClear = gs.mainmenu_button_contour(frameNegativePrompt, height=0, width=0, text="", image=presetNegativePromptClearImage, 
                                        command=lambda:ppo.ClearPresets(self._preset_negative_prompt_canvas))
    presetNegativePromptClear.element.grid(row=thisrow, column=1, stick="e")
    
    thisrow+=1
    _dummyFrame = ctk.CTkFrame(frameNegativePrompt)
    self._preset_negative_prompt_canvas = gs.mainmenu_buttoncanvas(_dummyFrame, width=305, height=50)
    _dummyFrame.grid(row=thisrow, columnspan=2, stick="w")

    thisrow+=1
    presetNegativePromptText = gs.mainmenu_inner_entry(frameNegativePrompt, width=280, placeholder_text="<Add preset negative prompt...>")
    presetNegativePromptText.element.bind("<Return>", lambda event: ppo.AddPresetPromptFromGUI(self, presetNegativePromptText.element, 
                                                                                    self._preset_negative_prompt_canvas, "negative"))
    presetNegativePromptText.element.grid(row=thisrow, column=0, stick="w", pady=5)
    
    presetNegativePromptButton = gs.mainmenu_button(frameNegativePrompt, height=10, width=40, text="Add", 
                                        command=lambda: ppo.AddPresetPromptFromGUI(self, presetNegativePromptText.element,
                                                                                self._preset_negative_prompt_canvas, "negative"))
    presetNegativePromptButton.grid(row=thisrow, column=1, stick="e")

    frameNegativePrompt.pack(padx=2, pady=2, ipadx=3, ipady=3, anchor="w", fill=tk.X)
    ######################################################################

    ######################### PARAMETERS FRAMES ###############################
    frameParams = gs.mainmenu_frame(TTI_main_frame, fg_color="#1e1e1e")
    
    subframeParams1 = gs.mainmenu_subframe(frameParams)

    guidanceLabel = gs.mainmenu_inner_label(subframeParams1, text="Guidance scale")
    guidanceLabel.element.pack(side="left", padx=2)
    
    guidanceEntry = gs.mainmenu_inner_entry(subframeParams1, width=40, starting_text="6", allowed_chars=r'^\d*\.?\d*$')
    self._TTIguidanceEntry = guidanceEntry.element
    guidanceEntry.element.pack(side="left", padx=2)

    istepsLabel = gs.mainmenu_inner_label(subframeParams1, text="Inference steps")
    istepsLabel.element.pack(side="left", padx=2)
    
    istepsEntry = gs.mainmenu_inner_entry(subframeParams1, width=40, starting_text="15", allowed_chars=r'^\d+$')
    self._TTIistepsEntry = istepsEntry.element
    istepsEntry.element.pack(side="left", padx=2)

    subframeParams1.pack(side="top", ipady=5, ipadx=5, padx=2, expand=True, fill=tk.X)

    subframeParams2 = gs.mainmenu_subframe(frameParams)

    seedLabel = gs.mainmenu_inner_label(subframeParams2, text="Seed")
    seedLabel.element.pack(side="left", padx=2)
    
    seedEntry = gs.mainmenu_inner_entry(subframeParams2, width=100, placeholder_text="<random>", allowed_chars=r'^\d+$')
    self._TTIseedEntry = seedEntry
    seedEntry.element.pack(side="left", padx=2)

    randomizeSeed = gs.mainmenu_button(subframeParams2, text="Use random seed", command=lambda:seedEntry.element.delete(0, 'end'))
    randomizeSeed.pack(side="left", padx=5)

    subframeParams2.pack(side="bottom", ipady=5, ipadx=5, padx=2, expand=True, fill=tk.X)
    frameParams.pack(padx=2, pady=2, ipadx=3, ipady=3, anchor="w", expand=True, fill=tk.X)

    
    lastFrameParams = gs.mainmenu_frame(TTI_main_frame, fg_color="#1e1e1e")

    schedulerLabel = gs.mainmenu_inner_label(lastFrameParams, text="Sampler")
    schedulerLabel.element.pack(side="left", padx=2)

    schedulerMenu = gs.mainmenu_optionmenu(lastFrameParams, width=150, initvalue="")
    self._TTIschedulerMenu = schedulerMenu
    # self._FillSchedulers(schedulerMenu)
    schedulerMenu.pack(side="left", padx=2)

    NSFWSwitch = gs.mainmenu_switch(lastFrameParams, text="Allow NSFW\ncontent",
                                initvalue="yes", onvalue="yes", offvalue="no")
    NSFWSwitch.element.pack(padx=2, pady=2)
    
    lastFrameParams.pack(ipady=5, ipadx=5, padx=2, anchor="w")

    ######################################################################

    TTI_main_frame.pack(side="left")
    TTI_main_frame.update_idletasks() # Other functions will depend upon accurate measurements of this widget, so we update it now.
    self._TTI_main_frame = TTI_main_frame
    
    # Put TTI_main_frame inside its containing canvas
    canvas.create_window((0, 0), window=TTI_main_frame, anchor=tk.NW)
    # Configure Canvas scrolling
    canvas.configure(yscrollcommand=scrollbar.set)
    # Make sure to recalculate the scrollbar's slider if TTI_main_frame ever changes
    TTI_main_frame.bind("<Configure>", on_canvas_configure)
    # Wait for TTI_main_frame to finish being built, and then call on_canvas_configure to recalculate the scrollbar's slider
    TTI_main_frame.after_idle(TTI_main_frame_final_actions)

    # Handle the MouseWheel event on all objects inside canvas to move the scrollbar
    bind_children_recursive(TTI_main_frame, "<MouseWheel>", canvas_on_mousewheel)

    # Add the Generate button frame
    generateFrame = ctk.CTkFrame(left_menu_parent_frame)
    self._generateButton = ctk.CTkButton(generateFrame, height=40, width=150, text="Generate!", font=("Arial", 18),
                                fg_color="#900020", command=lambda:self._generate_image(seed_number=seedEntry.element.get(), 
                                                    width=widthTextbox.element.get(), height=heightTextbox.element.get(),
                                                    prompt=promptTexbox.element.get("1.0", tk.END), 
                                                    negative_prompt=negative_promptTexbox.element.get("1.0", tk.END),
                                                    inference_steps=istepsEntry.element.get(), 
                                                    guidance_scale=guidanceEntry.element.get(), 
                                                    scheduler=schedulerMenu.get()))
    self._generateButton.pack(side="right", padx=2, pady=10)
    generateFrame.pack(fill=tk.X)

    
    # Create the bottom border image in the main canvas
    hor_border_FullHD_height = self._GetFullHDActualPixelWidthEquivalent(35)
    hor_border_height = self._GetScaledPixelSize(hor_border_FullHD_height) # Internal top/bottom border height
    bottomborder_image_original = Image.open(self._skin_path + "\\frame_bottom.png")
    image_aspect_ratio = bottomborder_image_original.height / bottomborder_image_original.width
    target_border_width = int(hor_border_height / image_aspect_ratio)
    bottomborder_image = ImageTk.PhotoImage(bottomborder_image_original.resize((target_border_width, hor_border_height), Image.ANTIALIAS).crop((0,0,self._left_menu_canvas.winfo_width() + scrollbar.winfo_width(), hor_border_height)))

    bottom_border_frame = ctk.CTkFrame(left_menu_parent_frame, width=0, height=0)
    bottom_border_image_label = ctk.CTkLabel(bottom_border_frame, image=bottomborder_image, text="")
    bottom_border_image_label.pack()
    bottom_border_frame.pack(fill=tk.X)

    # Finally, load the current TTI model preset
    _LoadCurrentTTImodelPreset(self)

def _FillTTIModelPresets(TotemGUI_instance):
    """
    Fills the model presets menu with a sorted list of all model presets in the TTI models JSON
    """
    # Since we can't import TotemGUI due to circular reference, make a "mini-cast" here
    from GUI import TotemGUI
    self:TotemGUI = TotemGUI_instance
    
    TTImodels_path = self.TTImodels_path
    targetWidget = self._TTImodelmenu
    currently_selected_model = targetWidget.get() # Get the currently selected model, if any
        
    # Load the Models -> TTI JSON into a dictionary
    existing_json = cf.load_json_from_file(TTImodels_path)
    
    # Populate modelPresets with all model names
    current_model_found = False
    modelPresets = []
    for item in existing_json['model']:
        modelPresets.append(item['name'])
        if item['name']==currently_selected_model:
            current_model_found = True
    
    if not current_model_found:
        targetWidget.set("")


    # Add modelPresets as the values of the target widget
    targetWidget.configure(values=sorted(modelPresets))

def _TTIModelPresetLoad(TotemGUI_instance, model_to_load):
    """
    Sets model_to_load as the current TTI model preset
    """
    # Since we can't import TotemGUI due to circular reference, make a "mini-cast" here
    from GUI import TotemGUI
    self:TotemGUI = TotemGUI_instance

    if (model_to_load != ""):
        # Save the TTI model preset as the default preset in the general settings
        settings_json = cf.load_json_from_file(self.general_settings_file)
        settings_json['TTI_model_preset'] = model_to_load
        cf.save_json_to_file(self.general_settings_file, settings_json)

        _LoadCurrentTTImodelPreset(self)

def _LoadCurrentTTImodelPreset(TotemGUI_instance):
    """
    Performs all actions related to the TTI menu for the active model preset.
    """
    
    # Since we can't import TotemGUI due to circular reference, make a "mini-cast" here
    from GUI import TotemGUI
    self:TotemGUI = TotemGUI_instance
    
    # Load the current TTI model preset from the JSON
    settings_json = cf.load_json_from_file(self.general_settings_file)
    
    if "TTI_model_preset" in settings_json:
        model_to_load = settings_json['TTI_model_preset']
    else:
        model_to_load = ""

    if len(model_to_load) > 0:
        # Repopulate the Schedulers options, now that the defaul preset is different
        self._FillSchedulers(self._TTIschedulerMenu)

        # Update the current model label
        currentModelLabel.element.configure(text=self._TotemLang.LangString("GUI_TTI_menu.modelframe.currentmodel") + ": " + model_to_load)