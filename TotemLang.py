class TotemLang():
    def __init__(self, language_code="EN_US") -> None:
        self.language_strings = self.LoadStrings(language_code)

    def LoadStrings(self, language_code):
        XlatedStrings = {
        'General.Apply': 'Apply',
        'General.ApplyChanges': 'Apply changes',
        'General.DiscardChanges': 'Discard changes',
        'General.GoBack': 'Go back',
        'General.Save': 'Save',
        'General.Cancel': 'Cancel',
        'General.Close': 'Close',
        'General.ReplyYES': 'YES',
        'General.Confirmation': 'Confirmation',
        'GUI_Settings.GeneralTitle': 'Settings', 
        'GUI_Settings.mainmenu_model': 'Model',
        'GUI_Settings.mainmenu_interface': "Interface",
        'GUI_Settings.model.tti': "Text to Image",
        'GUI_Settings.model.tti.delete_messagebox': "Enter %1 in the following textbox to delete the selected model preset",
        'GUI_Settings.model.tti.apply_successful_title': "Changes Applied",
        'GUI_Settings.model.tti.apply_successful_content': "All changes were successfully applied to model preset '%1'",
        'GUI_Settings.model.tti.somethingchanged_title': "Changes were made",
        'GUI_Settings.model.tti.somethingchanged_content': "If you perform this action, the changes you made will be lost. How do you want to proceed?",
        'GUI_Settings.model.tti.modelpresets': "Model Presets",
        'GUI_Settings.model.tti.general_intro': "General Options",
        'GUI_Settings.model.tti.general_isSDXL': "This preset is for SDXL models",
        'GUI_Settings.model.tti.name_label': "Model preset name",
        'GUI_Settings.model.tti.name_placeholder': "<Enter a name for this preset...>",
        'GUI_Settings.model.tti.mainmodel': "Main model path",
        'GUI_Settings.model.tti.mainmodel_placeholder': "<Enter the main path of the model...>",
        'GUI_Settings.model.tti.unet_optimization_label': "Choose the optimizations to use for this unet model",
        'GUI_Settings.model.tti.optimization_fp16': "Half precision weights (fp16)",
        'GUI_Settings.model.tti.optimization_safetensors': "Use safetensors",
        'GUI_Settings.model.tti.optimization_torchcompile': "Torch compile",
        'GUI_Settings.model.tti.optimization_vaetiling': "VAE tiling",
        'GUI_Settings.model.tti.optimization_xformers': "Xformers",
        'GUI_Settings.model.tti.optimization_seqCPUoffload': "Sequential CPU offload",
        'GUI_Settings.model.tti.optimization_modCPUoffload': "Model CPU offload",
        'GUI_Settings.model.tti.optimization_attention': "Attention slicing",
        'GUI_Settings.model.tti.vaemodel': "VAE model path",
        'GUI_Settings.model.tti.vaemodel_placeholder': "<Enter the path of the vae model...>",
        'GUI_Settings.model.tti.vaemodel_usevae': "Use the VAE specified above when using this preset",
        'GUI_Settings.model.tti.refinermodel': "Refiner model path",
        'GUI_Settings.model.tti.refinermodel_placeholder': "<Enter the path of the refiner model...>",
        'GUI_Settings.model.tti.refiner_optimization_label': "Choose the optimizations to use for this refiner model",
        'GUI_Settings.model.tti.refinermodel_userefiner': "Use the refiner specified above when using this preset",
        'GUI_Settings.model.tti.refinervaemodel': "Refiner's VAE model path",
        'GUI_Settings.model.tti.refinervaemodel_usevae': "Use the VAE specified above when using the refiner of this preset",
        'GUI_Settings.model.tti.newmodel_dialog_title': "Create new model preset",
        'GUI_Settings.model.tti.newmodel_dialog_preamble': "Enter the name of the new TTI model preset",
        'GUI_Settings.model.tti.newmodel_exists_title': "Model preset name already exists",
        'GUI_Settings.model.tti.newmodel_exists_content': "The model preset name you chose already exists! Choose a different one.",
        'GUI_Settings.model.tti.newmodel_emptyname_title' : "Name is empty",
        'GUI_Settings.model.tti.newmodel_emptyname_content' : "Please specify a name for this model preset",
        'GUI_TTI_menu.modelframe.modelpreset' : "Model Preset",
        'GUI_TTI_menu.modelframe.currentmodel' : "Current model preset"}
        
        return XlatedStrings

    def LangString(self, string_key, parameters=[]):
        """
        Returns the string that corresponds to string_key in the target language.\n
        If the string has parameters (i.e., "%1", "%2", etc.), replaces them with the values in the parameters argument.
        """
        final_string = self.language_strings[string_key]

        for i, value in enumerate(parameters):
            final_string = final_string.replace("%" + str(i+1), value)

        return final_string