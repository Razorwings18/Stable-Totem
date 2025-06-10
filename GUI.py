# Libraries for generation
from TTI import TextToImage

# Libraries for building GUI 
import rwCTk as rwctk
import tkinter as tk
from tkinter import messagebox, ttk
import customtkinter as ctk 
from PIL import ImageTk, Image
import GUIstyles as gs
import GUI_centertab_scripts
import GUI_Right_menu, GUI_TTI_menu, GUI_Topbar, TotemLang
from GUI_Settings import GUI_Settings

# Import auxiliary libraries
from typing import Literal
import re, ctypes, sys, time, os
import common_functions as cf

# Import libraries that break down this script into smaller scripts
import promptPresetOperations as ppo

##############################################
class ImgPlaceholderInfo():
    def __init__(self, GUI_instance:'TotemGUI'):
        self.GUI_instance = GUI_instance
        self.original_image = None
        
        # These are used to fill the TTI menu if requested
        self.seed = 0
        self.guidance = 0
        self.steps = 0
        self.prompt = ""
        self.prompt_preset_buttons = []
        self.negative_prompt = ""
        negative_prompt_preset_buttons = []
        self.scheduler = ""
        self.vae = False
    def configure(self, image, seed, guidance, steps, prompt, prompt_preset_buttons, negative_prompt, negative_prompt_preset_buttons,
                  scheduler, vae):
        self.original_image = image

        self.seed = seed
        self.guidance = guidance
        self.steps = steps
        self.prompt = prompt
        self.prompt_preset_buttons = prompt_preset_buttons
        self.negative_prompt = negative_prompt
        self.negative_prompt_preset_buttons = negative_prompt_preset_buttons
        self.scheduler = scheduler
        self.vae = vae

        self.GUI_instance._ResizePlaceholderImage(image)

class TotemGUI():
    def __init__(self, script_path) -> None:
        self._app = None
        
        # Do language stuff
        self._TotemLang = TotemLang.TotemLang()
        
        # Define useful paths
        self._script_path = script_path
        self._skin_path = script_path + "\\resources\\GUI-images\\skins\\mainskin"
        self.models_path = script_path + "\\models"
        self.TTImodels_path = self.models_path + "\\TTImodels.json"
        self.general_settings_file = script_path + "\\settings.json"


        # Define global widgets and variables
        self._current_mode:Literal["TTI"] = "TTI" # Currently selected mode

        self.realScreenSize = [] # Contains the real screen size in format [width, height]
        self.screenWidthCoefficient = 0 # Contains a width coefficient in relation to a 1920px monitor. E.g., 2.0 is a 3840px monitor.

        self._left_menu_parent_frame = None
        self._scrollable_left_menu_frame = None # Top-level frame that contains self._left_menu_canvas
        self._left_menu_canvas = None # Canvas of the left menu, which will contain left menu frames such as the TTI_main_frame
        self._left_menu_bottomborder = None # The ID if the bottom border image of the left menu
        self._TTI_main_frame = None # Frame that contains the TTI (left) menu
        self._image_placeholder = None # Reference to the ImgPlaceholderInfo instance
        self._TTIsteps = None
        
        self._TTImodelmenu = None # Option widget with the selected TTI model prest
        self._TTIseedEntry = None # The seed Entry widget in the TTI main menu
        self._TTIguidanceEntry = None # Guidance scale widget in the TTI main menu
        self._TTIistepsEntry = None
        self._TTIpromptTextbox = None # Prompt textbox (the element) in the TTI main menu
        self._TTInegative_promptTextbox = None
        self._TTIschedulerMenu = None
        
        self._preset_prompt_canvas = None # The preset prompt button canvas in the TTI main menu
        self._preset_negative_prompt_canvas = None # The negative preset prompt button canvas in the TTI main menu
        self._presetFileMenu = None
        self._generateButton = None # The generate button in the TTI main menu
        
        self._main_canvas = None # This is the canvas that will contain all GUI images
        self._top_bar_left_image = None # Top bar's left end image in _main_canvas
        self._top_bar_right_image = None # Top bar's right end image in _main_canvas
        self._top_bar_center_image = None # Top bar's center image in _main_canvas
        self._top_bar_center_image_source = None # The original image, which we need to resize when the window resizes
        self._preservedImages = {} # This stores a reference to "preserved images" to protect them from being garbage-collected

        self._imagebar_scrollbar_width = 0 # Width of the image bar's scrollbar
        self._imagebar_thumbnail:tk.Label = [] # List that will contain all Label widgets, which are effectively the individual thumbnails
        self._imagebar_canvas_frame = None # Required to be global for internal size calculations

        self._right_menu_parent_frame = None # Top-level frame of the right menu
        self._scrollable_right_menu_frame = None # Scrollable right menu frame (the one that contains _right_menu_canvas below)
        self._right_menu_canvas = None # This is the canvas that contains the imagebar's thumbnails
        #self._right_menu_frame = None # The inner frame of the right bar, where all menu items will go
        self._imagebar_thumbnails_frame = None # The thumbnails frame; the lowest-level thumbnail holder.
        self._imagebar_canvas = None # Canvas of the image bar inside _imagebar_thumbnails_frame, which directly contains the thumbnails
        self._imagebar_scroll_handler = None # Command pointing to the function of GUI_Right_menu that handles the mousewheel scrolling
        self._imagebar_scrollbar = None # Scrollbar of the imagebar

        # These will contain the components of the generated image (at the center of the screen)
        self._generated_image_canvas = None
        self._generated_image_topborder = None
        self._generated_image_bottomborder = None
        self._generated_image_leftborder = None
        self._generated_image_rightborder = None
        self._generated_image_original_image = None # Contains the PIL image, updated every time a new image is generated

        # These will contain the components of the center tab (attached to the generated image)
        self._centertab_frame = None # Main center tab frame
        self._centertab_subframe = None # Frame that contains all the buttons
        
        # These are the colors of the prompt preset buttons for each possible priority (weight). Each element is  [fg, hover, text]
        self._preset_button_color_per_priority = [["dodger blue", "navy", "white"], ["yellow", "goldenrod", "black"], ["red", "darkred", "white"]]
        
        # Text-to-image class instance to use for the various actions
        self._TTI = TextToImage(script_path, self.models_path, self.TTImodels_path, self.general_settings_file)
        # Settings class, which has everything related to settings
        self._Settings = GUI_Settings(self)

        # Initialize PromptPresetOperations
        ppo.Initialize(script_path=script_path)

    def _GetFullHDActualPixelWidthEquivalent(self, fullHD_pixel_size):
        """
        Returns the size in ACTUAL pixels at the current screen resolution that would be equivalent
        to those pixels in FullHD (1920x1080).\n
        E.g., if this screen's width is 3840 (twice the size of 1920), an input of 100px would output 200px.\n\n
        NOTE: This only uses the screen width for reference!!!
        """
        return int(fullHD_pixel_size * self.screenWidthCoefficient)

    def _GetFullHDFixedWidthPhotoImage(self, image_path, fullHD_width):
        """
        Returns a PhotoImage object with a width that is equivalent to the REAL fullHD_width pixels scaled for this screen.\n
        In other words, if this screen's width is twice 1920, and the fullHD_width argument is 100px, it will return an image that has
        a REAL (not scaled) width on screen of 200px, maintaining the aspect ratio.
        """
        target_image = Image.open(image_path)
        target_image_width = self._GetScaledPixelSize(self._GetFullHDActualPixelWidthEquivalent(fullHD_width))
        target_image_height = int(target_image_width * (target_image.size[1]/target_image.size[0]))
        return ImageTk.PhotoImage(target_image.resize((target_image_width, target_image_height), Image.ANTIALIAS))

    def _GetScaledPixelSize(self, actual_pixels: int):
        """
        TKinter uses the scaling factor set up in Windows. E.g., if the scaling factor is 125%,
        if we want the actual size on screen to be 125px, we must set the tkinter width to 100 ("scaled pixels").
        This returns that 100px.
        """
        if sys.platform == 'win32':
            return int(actual_pixels / (ctypes.windll.shcore.GetScaleFactorForDevice(0) / 100))
        else:
            return actual_pixels
    
    def _GetActualPixelSize(self, scaled_pixels: int):
        """
        TKinter uses the scaling factor set up in Windows. E.g., if the scaling factor is 125%,
        when winfo_width==100 ("scaled pixels"), the actual size on screen is 125px. This returns that 125px.
        """
        if sys.platform == 'win32':
            return int(scaled_pixels * (ctypes.windll.shcore.GetScaleFactorForDevice(0) / 100))
        else:
            return scaled_pixels

    def _GetRelativeSize(self, ctkObject: ctk.CTkBaseClass):
        """
        Returns the relative width of ctkObject\n
        E.g., this returns [0.5, 0.5] if ctkObject occupies half of its parent's size in each direction
        """
        return [(ctkObject.winfo_width() / ctkObject.master.winfo_width()), (ctkObject.winfo_height() / ctkObject.master.winfo_height())]

    def _BuildTTIPromptMenu(self):
        """
        Builds the Text-to-Image left-side menu.
        """
        GUI_TTI_menu._BuildTTIPromptMenu(self)
        self._left_menu_resizer()

    def _BuildRightMenu(self):
        """
        Build the right navigation bar.
        """
        GUI_Right_menu._BuildRightMenu(self)
        self._PopulateImageBar()

    def _MainWindowResized(self, event):
        """
        This is the main event handler for the main window's resize.\n
        Does all actions required when it is resized.
        """
        window_resized = True
        window_size = [self._app.winfo_width(), self._app.winfo_height()]

        # If the parent frame has not been resized since last time we checked, set window_resized to false, so that nothing is done
        # This is necessary because the event that triggers this is raised under many different circumstances
        if (hasattr(self._app, "last_window_size")):
            if (self._app.last_window_size == window_size):
                window_resized = False
        else:
            # The very first time this is run, it might be triggered by an incorrect event, so disregard the very first call
            window_resized = False
        
        # Window was resized. Do all necessary actions.
        if (window_resized):
            GUI_Topbar.topbar_resizer(self, event.width)
            self._left_menu_resizer()
            GUI_Right_menu.RightMenuResizer(self)
            self._ResizePlaceholderImage()

        # Update the last_window_size variable to the current window size, in preparation for the next time it is checked.
        self._app.last_window_size = [self._app.winfo_width(), self._app.winfo_height()]

    def _left_menu_resizer(self):
        # Calculate the menu's minimum clearance from the bottom of the window
        clearance = self._GetScaledPixelSize(self._GetFullHDActualPixelWidthEquivalent(30))
        # Calculate the target height (never smaller than 100)
        target_height = max(100, self._app.winfo_height() - self._left_menu_parent_frame.winfo_y() - clearance)

        # Get the direct child frames of _left_menu_parent_frame
        child_frames = [self._left_menu_parent_frame.nametowidget(child_name) for child_name in self._left_menu_parent_frame.winfo_children() if (isinstance(self._left_menu_parent_frame.nametowidget(child_name), tk.Frame) or isinstance(self._left_menu_parent_frame.nametowidget(child_name), ctk.CTkFrame))]

        # Iterate through the direct child frames of _left_menu_parent_frame. Since only the scrollable frame will need to be resized,
        # we remove the size of all other fixed frames from the scrollable frame's target height
        for frame in child_frames:
            if not hasattr(frame, "scrollable"):
                frame.update()
                target_height -= frame.winfo_height()

        # If the TTI menu is smaller than the target height, then adopt the size of TTI menu
        if (self._TTI_main_frame.winfo_height()<target_height):
            self._left_menu_canvas.configure(height=self._TTI_main_frame.winfo_height())
        else:
            self._left_menu_canvas.configure(height=target_height)

    def image_loaded(self):
        """
        What does this even do? This, and what scrum masters do all day, are the greatest mysteries of our time.
        """
        self._loaded.set(True)

    def _BuildMainWindow(self):
        # Build the app's main window
        self._app = tk.Tk()
        app = self._app

        # Fill the real screen size (in real px) and screenWidthCoefficient now, so we can get it out of the way
        self.realScreenSize = [self._GetActualPixelSize(app.winfo_screenwidth()), self._GetActualPixelSize(app.winfo_screenheight())]
        self.screenWidthCoefficient = self._GetActualPixelSize(app.winfo_screenwidth()) / 1920
        
        app.configure(bg='black')
        app.geometry(f"{self._GetScaledPixelSize(1900)}x{self._GetScaledPixelSize(1000)}")
        app.title("Stable Totem")
        app.state('zoomed')  # Set the window state to maximized
        app.update_idletasks()
        ctk.set_appearance_mode("dark")

        # Build the "main canvas". This will be used to show all GUI images that use alpha transparency
        # (since canvases are the only widgets that can use transparency)
        self._main_canvas = tk.Canvas(app, bg="black", highlightthickness=0)
        self._main_canvas.place(x=0, y=0, anchor="nw", relwidth=1, relheight=1)
        self._main_canvas.update_idletasks() # Update now so other methods will have access to its information

    def _BuildBackground(self):
        """
        Must be run after _BuildTopBar since background placement uses the top bar's position as reference
        """
        # Load the background image
        image = self._GetFullHDFixedWidthPhotoImage(f"{self._skin_path}\\background_dark.png", 950)
        self._backgroundimage = image # We need to store the image in a global variable or it gets garbage collected and won't show!!! LOL!
        
        # Calculate the desired width for the tiled background (e.g., the screen width)
        desired_width = int(self._app.winfo_screenwidth())

        # Get information on the position of the top bar. It will be used as a reference point to place the background images.
        x1, y1, x2, y2 = self._main_canvas.bbox(self._top_bar_left_image)

        # Tile the image horizontally
        x_offset = -self._GetFullHDActualPixelWidthEquivalent(110)
        for x in range(x_offset, desired_width, image.width()):
            bgImage = self._main_canvas.create_image(x, y2 - ((y2 - y1) / 4), image=image, anchor="nw")
            self._main_canvas.lower(bgImage)

    def GenerateBaseGUI(self):
        self._BuildMainWindow() # This builds the main window, including loading the top level widget into self._app
        GUI_Topbar.BuildTopBar(self)
        self._BuildBackground() # Must be run after _BuildTopBar since background placement uses the top bar's position as reference
        app = self._app
        
        # Add an event handler for when the window resizes. Useful to handle anything that needs to be done when it does.
        app.bind('<Configure>', self._MainWindowResized, add="+")
        
        self._BuildTTIPromptMenu()
        self._BuildRightMenu()
        
        app.mainloop()

    def _imagebar_leftclick(self, thumbnail_index):
        """
        Load the imagebar's image that was clicked as the main image being worked on.
        """
        # If the placeholder manager instance has not yet been created, create it now
        if (self._image_placeholder==None):
            self._image_placeholder=ImgPlaceholderInfo(self)

        # Load the image that corresponds to the thumbnail
        image = Image.open(self._imagebar_thumbnail[thumbnail_index].image_path)

        # Retrieve specific metadata values using the keys used while saving
        seed = int(image.info.get("seed", "0"))
        guidance_scale = float(image.info.get("guidance", "7"))
        num_inference_steps = int(image.info.get("steps", "20"))
        prompt = image.info.get("prompt", "")
        negative_prompt = image.info.get("negative_prompt", "")
        scheduler_name = image.info.get("scheduler", "")
        use_vae = True if (image.info.get("vae", "False")=="True") else False
        
        elements = image.info.get('prompt_preset', "").split('||')
        try:
            prompt_preset_buttons = [[pair.split('|')[0], int(pair.split('|')[1])] for pair in elements]
        except:
            prompt_preset_buttons = []

        elements = image.info.get('negative_prompt_preset', "").split('||')
        try:
            negative_prompt_preset_buttons = [[pair.split('|')[0], int(pair.split('|')[1])] for pair in elements]
        except:
            negative_prompt_preset_buttons = []

        self._image_placeholder.configure(image=image, seed = seed, guidance = guidance_scale, steps = num_inference_steps,
                                      prompt = str(prompt), prompt_preset_buttons = prompt_preset_buttons, 
                                      negative_prompt = str(negative_prompt), negative_prompt_preset_buttons = negative_prompt_preset_buttons,
                                      scheduler = scheduler_name, vae = use_vae)
        
    def _PopulateImageBar(self, new_image = None):
        """
        Populates the image bar with thumbnails
        """
        
        # Bring global variables locally for ease of use
        thumbnails_frame = self._imagebar_thumbnails_frame
        thumbnail_reference_frame = self._right_menu_canvas
        # Set the generated image folder path
        image_folder = f"{self._script_path}\\generated images"
        # Set the padding between thumbnail images
        imagebar_thumb_padding_x = self._GetScaledPixelSize(self._GetFullHDActualPixelWidthEquivalent(3))
        imagebar_thumb_padding_y = self._GetScaledPixelSize(self._GetFullHDActualPixelWidthEquivalent(3))
        # Set the images per row
        num_images_per_row = 4

        def resize_image(image_path, width, height):
            img = Image.open(image_path)
            img.thumbnail((width, height))
            return ImageTk.PhotoImage(img)

        def calculate_thumbnail_size(num_images_per_row, frame_width, frame_height, padx, pady):
            thumbnail_width = frame_width // num_images_per_row
            thumbnail_width -= (padx * 2)
            thumbnail_height = thumbnail_width
            return thumbnail_width, thumbnail_height
        
        thumbnail_width, thumbnail_height = calculate_thumbnail_size(num_images_per_row, thumbnail_reference_frame.winfo_width(),
                                                                     thumbnail_reference_frame.winfo_height(), imagebar_thumb_padding_x, 
                                                                     imagebar_thumb_padding_y)

        # Save the current scrollbar position to come back to it after repopulating the imagebar
        current_scrollbar_pos = self._imagebar_scrollbar.get()[0]

        if (new_image == None) or len(self._imagebar_thumbnail)==0:
            # Clear all previous thumbnails
            for i in self._imagebar_thumbnail:
                i.destroy()
            self._imagebar_thumbnail.clear()

            images_in_imagefolder = [file for file in os.listdir(image_folder) if file.endswith('.png')]
            for i, filename in enumerate(sorted(images_in_imagefolder, reverse=True)):
                image_path = os.path.join(image_folder, filename)

                thumbnail = resize_image(image_path, thumbnail_width, thumbnail_height)

                thumbnail_label = tk.Label(thumbnails_frame, image=thumbnail, borderwidth=0, cursor="hand2")
                thumbnail_label.image = thumbnail  # To prevent garbage collection
                thumbnail_label.image_path = image_path # Pointer to the original image. We'll need this for many operations later.
                thumbnail_label.grid(row=i // num_images_per_row, column=i % num_images_per_row, padx=imagebar_thumb_padding_x, pady=imagebar_thumb_padding_y)
                self._imagebar_thumbnail.append(thumbnail_label)
                thumbnail_label.index = len(self._imagebar_thumbnail)-1 # Stores the index of this thumbnail in self._imagebar_thumbnail
                # Bind the mouse wheel event so that the image bar scrolls when the moust pointer is on top of this thumbnail
                thumbnail_label.bind("<MouseWheel>", self._imagebar_scroll_handler)
                # And bind the left click to perform the left-click action
                thumbnail_label.bind("<Button-1>", lambda event, index=thumbnail_label.index: self._imagebar_leftclick(index))
            
            thumbnails_frame.update_idletasks()

            # Once all thumbnails have finished loading into the canvas, run self._imagebar_restore_position
            thumbnails_frame.after_idle(self._imagebar_restore_position, current_scrollbar_pos)
        else:
            # A new image is being loaded; no need to reload everything. First, we add a new thumbnail at the end with the very last image.
            # Then, we traverse self._imagebar_thumbnail back to front, copying the previous item to the next. Last, we add the new image
            # to the first element.
            # This is much faster than reloading everything from disk.
            
            # So, first, create a new label to put the very last thumbnail
            previous_object = self._imagebar_thumbnail[-1] # -1 means the 1st item from the very end (i.e.g, the last element)
            thumbnail_label = tk.Label(thumbnails_frame, image=previous_object.image, borderwidth=0, cursor="hand2")
            thumbnail_label.image = previous_object.image  # To prevent garbage collection
            thumbnail_label.image_path = previous_object.image_path # Move this information to this object too
            self._imagebar_thumbnail.append(thumbnail_label)
            # Place it at the very end where it should be
            thumbnail_label.index = len(self._imagebar_thumbnail)-1 # This is the index of the object we just created in _imagebar_thumbnail
            i = thumbnail_label.index
            thumbnail_label.grid(row=i // num_images_per_row, column=i % num_images_per_row, padx=imagebar_thumb_padding_x, pady=imagebar_thumb_padding_y)
            thumbnails_frame.update_idletasks()
            # Bind the mouse wheel event so that the image bar scrolls when the mouse pointer is on top of this thumbnail
            thumbnail_label.bind("<MouseWheel>", self._imagebar_scroll_handler)
            # And bind the left click to perform the left-click action
            thumbnail_label.bind("<Button-1>", lambda event, index=thumbnail_label.index: self._imagebar_leftclick(index))
            self._imagebar_thumbnail
            # Finally, run self._imagebar_restore_position, since the right bar may need to grow because of the new thumbnail
            thumbnails_frame.after_idle(self._imagebar_restore_position, current_scrollbar_pos)
            
            # And then we go back to front and move the previous image to the next object, except for the last element
            for index, i in enumerate(self._imagebar_thumbnail[::-1]):
                if index > (len(self._imagebar_thumbnail)-2):
                    # Handle the last element (actually the first, since we're traversing the list backwards)
                    previous_object = None
                    
                    images_in_imagefolder = [file for file in os.listdir(image_folder) if file.endswith('.png')]
                    image_path = os.path.join(image_folder, sorted(images_in_imagefolder, reverse=True)[0])
                    thumbnail = resize_image(image_path, thumbnail_width, thumbnail_height)
                    i.configure(image=thumbnail)
                    i.image = thumbnail
                    i.image_path = image_path
                else:
                    previous_object = self._imagebar_thumbnail[-(index + 2)]
                    i.configure(image=previous_object.image)
                    i.image = previous_object.image
                    i.image_path = previous_object.image_path

    def _imagebar_restore_position(self, pos):
        """
        Resizes the right menu, since it may need to grow as new thumbnails are added.\n
        Then, updates the scrollbar's slider based on the new canvas size and restores its position to where 
        it was before reloading all thumbnails.
        """
        # Resize the right menu to the right size
        GUI_Right_menu.RightMenuResizer(self)
        
        canvas = self._right_menu_canvas
        # Update the scrollbar slider to the new canvas size
        canvas.configure(scrollregion=canvas.bbox("all"))
        # Move the scrollbar to the position it was before reloading all thumbnails
        canvas.yview_moveto(pos)
        self._imagebar_scrollbar.set(*canvas.yview())
    
    def _ResizePlaceholderImage(self, source_image=None):
        # If the placeholder was not yet built and a new image (source_image) will be displayed in it, build it before we do anything.
        if self._generated_image_canvas == None:
            if source_image == None:
                return
            else:
                self._BuildPlaceholder()
        
        # If a new source_image is being loaded, use that as the main image. Otherwise, use the image that was already loaded.
        if (source_image!=None):
            myImage = source_image
            self._generated_image_original_image = source_image
        else:
            myImage = self._generated_image_original_image

        side_border_FullHD_width = self._GetFullHDActualPixelWidthEquivalent(43)
        hor_border_FullHD_height = self._GetFullHDActualPixelWidthEquivalent(35)
        clearance_width = self._GetScaledPixelSize(self._GetFullHDActualPixelWidthEquivalent(100)) # Outer space to the right and left
        clearance_height = self._GetScaledPixelSize(self._GetFullHDActualPixelWidthEquivalent(30)) # Outer space to the top and bottom
        side_border_width = self._GetScaledPixelSize(side_border_FullHD_width) # Internal side border width
        hor_border_height = self._GetScaledPixelSize(hor_border_FullHD_height) # Internal top/bottom border height
        img_display_canvas = self._generated_image_canvas
        # Set the minimum size the generated image frame can have. It will never be resized smaller than this.
        min_frame_size = [self._GetScaledPixelSize(self._GetFullHDActualPixelWidthEquivalent(100)),
                          self._GetScaledPixelSize(self._GetFullHDActualPixelWidthEquivalent(100))]

        # Determine the maximum width and height the image frame can occupy
        main_frame_right_x = (self._left_menu_parent_frame.winfo_x() + self._left_menu_parent_frame.winfo_width()) # X coord of main frame's right edge
        max_frame_width = self._right_menu_parent_frame.winfo_x() - main_frame_right_x - (clearance_width * 2)
        _, _, _, y2 = self._main_canvas.bbox(self._top_bar_left_image)
        max_frame_height = self._app.winfo_height() - y2 - (clearance_height * 2)
        
        # Make sure width and height are never less than the minimum allowed
        max_frame_width = max(max_frame_width, min_frame_size[0])
        max_frame_height = max(max_frame_height, min_frame_size[1])
        
        # Determine the coordinates of the exact center of the image frame
        centercoords = [(max_frame_width / 2) + main_frame_right_x + clearance_width, (max_frame_height / 2) + y2 + clearance_height]

        # Calculate the original image's width and height
        original_width = myImage.width
        original_height = myImage.height

        # Calculate the available space inside the inner borders
        inner_width = max_frame_width - 2 * side_border_width
        inner_height = max_frame_height - 2 * hor_border_height

        # Calculate the scale factor to maintain aspect ratio
        scale_factor = min(inner_width / original_width, inner_height / original_height)

        # Calculate the displayed image's width and height after scaling
        displayed_width = int(original_width * scale_factor)
        displayed_height = int(original_height * scale_factor)
        
        # Obtain the scaled image that fits in the canvas
        scaledImage = myImage.resize((displayed_width, displayed_height), Image.ANTIALIAS)
        
        # Calculate the final canvas dimensions considering image size and inner borders
        canvas_width = min(max_frame_width, displayed_width + 2 * side_border_width)
        canvas_height = min(max_frame_height, displayed_height + 2 * hor_border_height)

        # Calculate the top-left coordinates to center the canvas
        x_center = centercoords[0]
        y_center = centercoords[1]
        x1 = x_center - (canvas_width // 2)
        y1 = y_center - (canvas_height // 2)

        # Create the canvas with adjusted dimensions
        img_display_canvas.configure(width=canvas_width, height=canvas_height)
        img_display_canvas.place(x=x1, y=y1, anchor="nw")

        # Add the border images
        # Top
        topborder_image = ImageTk.PhotoImage(Image.open(self._skin_path + "\\frame_top.png").resize((canvas_width, hor_border_height), Image.ANTIALIAS))
        img_display_canvas.itemconfig(self._generated_image_topborder, image=topborder_image, anchor="nw")
        img_display_canvas.coords(self._generated_image_topborder, 0, 0)
        self._preservedImages['miB' + str(self._generated_image_topborder)] = topborder_image
        # Bottom
        bottomborder_image = ImageTk.PhotoImage(Image.open(self._skin_path + "\\frame_bottom.png").resize((canvas_width, hor_border_height), Image.ANTIALIAS))
        img_display_canvas.itemconfig(self._generated_image_bottomborder, image=bottomborder_image, anchor="sw")
        img_display_canvas.coords(self._generated_image_bottomborder, 0, canvas_height)
        self._preservedImages['miB' + str(self._generated_image_bottomborder)] = bottomborder_image
        # Left
        side_border_height = canvas_height - (hor_border_height * 2)
        leftborder_image = ImageTk.PhotoImage(Image.open(self._skin_path + "\\frame_left.png").resize((side_border_width, side_border_height), Image.ANTIALIAS))
        img_display_canvas.itemconfig(self._generated_image_leftborder, image=leftborder_image, anchor="nw")
        img_display_canvas.coords(self._generated_image_leftborder, 0, hor_border_height)
        self._preservedImages['miB' + str(self._generated_image_leftborder)] = leftborder_image
        # Right
        rightborder_image = ImageTk.PhotoImage(Image.open(self._skin_path + "\\frame_right.png").resize((side_border_width, side_border_height), Image.ANTIALIAS))
        img_display_canvas.itemconfig(self._generated_image_rightborder, image=rightborder_image, anchor="ne")
        img_display_canvas.coords(self._generated_image_rightborder, canvas_width, hor_border_height)
        self._preservedImages['miB' + str(self._generated_image_rightborder)] = rightborder_image

        # Display the image inside the canvas
        scaledPhotoImage = ImageTk.PhotoImage(scaledImage)
        img_display_canvas.itemconfig(self._generated_image_object, image=scaledPhotoImage)
        img_display_canvas.coords(self._generated_image_object, int(canvas_width / 2), int(canvas_height / 2))
        self._preservedImages['mi' + str(self._generated_image_object)] = scaledPhotoImage
        
        # Move the centertab menu to its new position
        self._centertab_frame.update()
        self._centertab_frame.place(x=int(x1 + canvas_width - side_border_width), y=int(y1), anchor="nw")
        self._centertab_frame.lift()
    
    def _BuildPlaceholder(self):
        """
        Creates the placeholder image's objects. Called by _ResizePlaceholderImage when needed.
        """
        self._generated_image_canvas = tk.Canvas(self._app, highlightthickness=0)
        
        self._generated_image_topborder = self._generated_image_canvas.create_image(0, 0, image=tk.PhotoImage(), anchor="nw")
        self._generated_image_bottomborder = self._generated_image_canvas.create_image(0, 0, image=tk.PhotoImage(), anchor="sw")
        self._generated_image_leftborder = self._generated_image_canvas.create_image(0, 0, image=tk.PhotoImage(), anchor="nw")
        self._generated_image_rightborder = self._generated_image_canvas.create_image(0, 0, image=tk.PhotoImage(), anchor="ne")
        
        self._generated_image_object = self._generated_image_canvas.create_image(0, 0, image=tk.PhotoImage())

        GUI_centertab_scripts.BuildPlaceholderCentertab(self)
        GUI_centertab_scripts.PopulatePlaceholderCentertab(self)
    
    def _generate_image(self, width, height, prompt, negative_prompt, seed_number, inference_steps, guidance_scale, scheduler):
        # We'll need to know the inference steps later for progress bar calculations, so we store it
        self._TTIsteps = inference_steps

        # Make sure that all requirements are met to start generating
        general_settings = cf.load_json_from_file(self.general_settings_file)

        if not ("TTI_model_preset" in general_settings):
            messagebox.showinfo("Cannot generate image", "Cannot generate image. Model preset not loaded.")
            return

        if (guidance_scale!="") and (inference_steps!=""):
            # Disable the generate button so it's not pressed while the image is processing
            self._generateButton.configure(state="disabled", text="Generating...")
            
            # Set the target object where the generated image will be shown
            if (self._image_placeholder==None):
                self._image_placeholder=ImgPlaceholderInfo(self)
            target_image_object = self._image_placeholder
            
            # Remove any escape characters from the prompts
            prompt = prompt.translate(str.maketrans('', '', '\n\r\t'))
            negative_prompt = negative_prompt.translate(str.maketrans('', '', '\n\r\t'))

            # Make sure width and height are either an int or None
            if width=="":
                width=None
            else:
                width=int(width)
            if height=="":
                height=None
            else:
                height=int(height)

            # Generate the image
            self._TTI.TTI_Generate(width=width, height=height, target_image_object=target_image_object, seed_number=seed_number, 
                                   prompt=prompt, negative_prompt=negative_prompt,
                                   inference_steps=inference_steps, guidance_scale=guidance_scale,
                                   process_finished_callable=self._GenerationEnded, progressCallable=self._GenerationProgress, 
                                   scheduler_name=scheduler, preset_prompt_canvas=self._preset_prompt_canvas,
                                   preset_negative_prompt_canvas=self._preset_negative_prompt_canvas)
        else:
            messagebox.showinfo("Cannot generate image", "Cannot generate image. Make sure that values for Guidance Scale and Inference Steps have been entered.")
    
    def _GenerationProgress(self, step, timestep, latents):
        # If the progressbar object (self._generation_progressbar) does not exist, create it for this process
        # It will be destroyed once the process is completed
        if not hasattr(self, "_generation_progressbar"):
            self._generation_progressbar = ctk.CTkProgressBar(self._app, orientation="horizontal")
            # I need to run "place" once, or otherwise GetRelativeWidth doesn't report the width of the progressbar correctly
            self._generation_progressbar.place(relx=0.5, rely=0.5)
            # Now that I can use GetRelativeWidth, place it again centered on its container
            self._generation_progressbar.place(relx=0.5-(self._GetRelativeSize(self._generation_progressbar)[0]/2), rely=0.5) #
            # Make sure the progressbar is on top
            self._generation_progressbar.lift()
        
        current_progress = step / int(self._TTIsteps)
        self._generation_progressbar.set(current_progress) # Update the progress bar as per the current step in the generation

        # Once the process is complete, we'll destroy the progressbar object. This process isn't called for the last step,
        # so we'll destroy it at _TTIsteps-1
        if (step == int(self._TTIsteps)-1):
            self._generation_progressbar.destroy()
            del self._generation_progressbar

    def _GenerationEnded(self):
        # Repopulate the image bar, which may now include the newly generated image
        self._PopulateImageBar(self._image_placeholder.original_image)
        
        # Re-enable the generate button that was disabled while the image was being generated
        self._generateButton.configure(state="normal", text="Generate!")

    def _FillSchedulers(self, target_control: ctk.CTkOptionMenu):
        compatible_schedulers = self._TTI.GetCompatibleSchedulers()
        if (compatible_schedulers != None):
            target_control.configure(values=compatible_schedulers)
        else:
            target_control.configure(values=[])

    def _UpdatePresetButtonColors(self, button):
            button.configure(fg_color = self._preset_button_color_per_priority[button.priority][0],
                            hover_color = self._preset_button_color_per_priority[button.priority][1],
                            text_color=self._preset_button_color_per_priority[button.priority][2])

    def _PresetPromptLeftClick(self, clickedButton:ctk.CTkButton):
        if (clickedButton.priority < (len(self._preset_button_color_per_priority)-1)):
            clickedButton.priority += 1
            self._UpdatePresetButtonColors(clickedButton)

    def _PresetPromptRightClick(self, clickedButton):
        if (clickedButton.priority > 0):
            clickedButton.priority -= 1
            self._UpdatePresetButtonColors(clickedButton)
        else:
            self._preset_prompt_canvas.remove_button(clickedButton)

    def _PresetNegativePromptLeftClick(self, clickedButton):
            if (clickedButton.priority < (len(self._preset_button_color_per_priority)-1)):
                clickedButton.priority += 1
                self._UpdatePresetButtonColors(clickedButton)

    def _PresetNegativePromptRightClick(self, clickedButton):
        if (clickedButton.priority > 0):
            clickedButton.priority -= 1
            self._UpdatePresetButtonColors(clickedButton)
        else:
            self._preset_negative_prompt_canvas.remove_button(clickedButton)
    
    def _preventCRTAB_Entry(self, event):
        # Get the pressed key
        key = event.keysym
        # Check if it's a carriage return or tab
        if key == "Return":
            # Ignore the event by returning "break"
            return "break"
        elif key == "Tab":
            if (event.state & 1):
                #Shift-Tab pressed, focus on the previous control
                event.widget.tk_focusPrev().focus()
                return
            else:
                # Tab pressed, focus on the next control
                event.widget.tk_focusNext().focus()
                # And make sure the TAB key is disregarded in the textbox
                return "break"