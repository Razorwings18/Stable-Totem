import customtkinter as ctk
import tkinter as tk
import GUIstyles as gs
import GUI_Tooltip

def BuildPlaceholderCentertab(self):
    # Define widget sizes using real pixels on screen at 1920x1080
    top_border_width = 63
    bottom_border_width = 63
    
    mainFrame = ctk.CTkFrame(self._app)
    
    top_border_image = self._GetFullHDFixedWidthPhotoImage(f"{self._skin_path}\\centertab\\centerbar_top_border.png", top_border_width)
    top_border = ctk.CTkLabel(mainFrame, text="", image=top_border_image)
    top_border.pack()

    subframe = gs.centertab_subframe(mainFrame)
    # subframe's contents will be added dynamically at a later time
    subframe.pack(expand=True, fill=tk.X)
    self._centertab_subframe = subframe

    bottom_border_image = self._GetFullHDFixedWidthPhotoImage(f"{self._skin_path}\\centertab\\centerbar_bottom_border.png", bottom_border_width)
    bottom_border = ctk.CTkLabel(mainFrame, text="", image=bottom_border_image)
    bottom_border.pack()

    #mainFrame.place(relx=0.5, rely=0.5)
    self._centertab_frame = mainFrame

def PopulatePlaceholderCentertab(self):
    button_width = 35

    subframe = self._centertab_subframe
    
    # Remove all widgets from inside the subframe
    for widget in subframe.winfo_children():
        widget.destroy()
    
    if (self._current_mode == "TTI"):
        # Use seed button
        seed_button_image = self._GetFullHDFixedWidthPhotoImage(f"{self._skin_path}\\centertab\\icon-seed.png", button_width)
        seed_button = gs.centertab_button(subframe, image=seed_button_image, command=lambda:xferLastSeed(self))
        seed_button.pack(expand=True, fill=tk.X)
        seed_button.tooltip = GUI_Tooltip.Tooltip(seed_button, "Use this image (seed) as a base for\n subsequent image generations")

        # Load prompt info button
        populate_prompt_button_image = self._GetFullHDFixedWidthPhotoImage(f"{self._skin_path}\\centertab\\icon-prompt.png", button_width)
        populate_prompt_button = gs.centertab_button(subframe, image=populate_prompt_button_image, command=lambda:populate_prompt(self))
        populate_prompt_button.pack(expand=True, fill=tk.X)
        populate_prompt_button.tooltip = GUI_Tooltip.Tooltip(populate_prompt_button, "Populate all fields with this image's\nprompt parameters.")


def xferLastSeed(GUI_instance):
    GUI_instance._TTIseedEntry.element.delete(0, "end")
    GUI_instance._TTIseedEntry.element.insert(0, GUI_instance._image_placeholder.seed)

def populate_prompt(GUI_instance_source):
    """
    Populates the TTI menu with the information of the image that is currently being displayed.\n
    This information was previously loaded into properties of the image's placeholder.
    """
    from tkinter import messagebox
    result = messagebox.askyesno("Retrieve prompting parameters", "This will replace all your current prompt parameters with the ones used to generate this image. Continue?", icon = "warning")
        
    if result:
        import promptPresetOperations as ppo
        
        # Since we can't import TotemGUI due to circular reference, make a "mini-cast" here
        from GUI import TotemGUI
        GUI_instance:TotemGUI = GUI_instance_source

        image_object = GUI_instance._image_placeholder
        
        GUI_instance._TTIguidanceEntry.delete(0,"end")
        GUI_instance._TTIguidanceEntry.insert(0, image_object.guidance if float(image_object.guidance)-int(image_object.guidance)!=0 else str(int(image_object.guidance)))
        
        GUI_instance._TTIistepsEntry.delete(0,"end")
        GUI_instance._TTIistepsEntry.insert(0, image_object.steps)
        
        GUI_instance._TTIpromptTextbox.delete(0.0, "end")
        GUI_instance._TTIpromptTextbox.insert(0.0, image_object.prompt)

        GUI_instance._preset_prompt_canvas.clear()
        for element in image_object.prompt_preset_buttons:
            ppo.AddPresetPrompt(GUI_instance, element[0], GUI_instance._preset_prompt_canvas, "positive", int(element[1]))
        
        GUI_instance._TTInegative_promptTextbox.delete(0.0, "end")
        GUI_instance._TTInegative_promptTextbox.insert(0.0, image_object.negative_prompt)

        GUI_instance._preset_negative_prompt_canvas.clear()
        for element in image_object.negative_prompt_preset_buttons:
            ppo.AddPresetPrompt(GUI_instance, element[0], GUI_instance._preset_negative_prompt_canvas, "negative", int(element[1]))
        
        GUI_instance._TTIschedulerMenu.set(image_object.scheduler)
        """
        image_object.vae = use_vae
        """


