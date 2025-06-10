import tkinter as tk
import customtkinter as ctk 
from PIL import ImageTk, Image
import GUIstyles as gs
import promptPresetOperations as ppo
import common_functions as cf

def _BuildRightMenu(TotemGUI_instance):
    """
    Builds the TTI left-side menu.\n
    There will be one frame with the attribute ".scrollable" that will be resizable when the main window is resized;
    all other frames will remain the same size.
    """

    # Since we can't import TotemGUI due to circular reference, make a "mini-cast" here
    from GUI import TotemGUI
    self:TotemGUI = TotemGUI_instance

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
            cf.LogEntry(title="Cannot bind mousewheel to _imagebar_frame child", message=f"Widget {widget} does not support MouseWheel binding", 
                        type="info", show_messagebox=False)
        for child in widget.winfo_children():
            bind_children_recursive(child, event, callback)

    def _thumbnails_frame_final_actions():
        canvas.configure(width=_thumbnails_frame.winfo_width())
        on_canvas_configure(None)
    
    right_menu_parent_frame = ctk.CTkFrame(self._app, width=0, height=0)
    self._right_menu_parent_frame = right_menu_parent_frame
    right_menu_parent_frame.place(x=self._app.winfo_width(), y=self._GetScaledPixelSize(self._GetFullHDActualPixelWidthEquivalent(143)),
                                  anchor="ne")
    
    scrollable_imagebar_frame = ctk.CTkFrame(right_menu_parent_frame, width=0, height=0, fg_color="#1e1e1e")
    scrollable_imagebar_frame.scrollable = True # This'll be used to tell the window resizer that this frame can be shrunk
    self._scrollable_right_menu_frame = scrollable_imagebar_frame
    scrollable_imagebar_frame.pack()

    canvas = tk.Canvas(scrollable_imagebar_frame, bg="black", width=0, height=0, highlightthickness=0)
    self._right_menu_canvas = canvas
    canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    scrollbar = ctk.CTkScrollbar(scrollable_imagebar_frame, orientation=tk.VERTICAL, command=on_scrollbar_move, fg_color="#1c130e", 
                                 button_color="#ddb27f", button_hover_color="#ba9a74")
    self._imagebar_scrollbar = scrollbar
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    _thumbnails_frame = ctk.CTkFrame(canvas, fg_color="black")
    self._imagebar_thumbnails_frame = _thumbnails_frame
    
    ############################## IMAGE BAR ########################################
    left_border_width = self._GetScaledPixelSize(self._GetFullHDActualPixelWidthEquivalent(43))
    internal_frame_width = self._GetScaledPixelSize(self._GetFullHDActualPixelWidthEquivalent(461)) - left_border_width
    _thumbnails_frame.configure(width=internal_frame_width)
    #################################################################################
    
    _thumbnails_frame.pack(side="left")
    _thumbnails_frame.update_idletasks() # Other functions will depend upon accurate measurements of this widget, so we update it now.
    self._imagebar_thumbnails_frame = _thumbnails_frame
    
    # Put _thumbnails_frame inside its containing canvas
    canvas.create_window((0, 0), window=_thumbnails_frame, anchor=tk.NW)
    # Configure Canvas scrolling
    canvas.configure(yscrollcommand=scrollbar.set)
    # Make sure to recalculate the scrollbar's slider if _thumbnails_frame ever changes
    _thumbnails_frame.bind("<Configure>", on_canvas_configure)
    # Wait for _thumbnails_frame to finish being built, and then call on_canvas_configure to recalculate the scrollbar's slider
    _thumbnails_frame.after_idle(_thumbnails_frame_final_actions)

    # Handle the MouseWheel event on all objects inside canvas to move the scrollbar
    self._imagebar_scroll_handler = canvas_on_mousewheel
    bind_children_recursive(_thumbnails_frame, "<MouseWheel>", self._imagebar_scroll_handler)

    # Create the bottom border image in the main canvas
    hor_border_FullHD_height = self._GetFullHDActualPixelWidthEquivalent(35)
    hor_border_height = self._GetScaledPixelSize(hor_border_FullHD_height) # Internal top/bottom border height
    bottomborder_image_original = Image.open(self._skin_path + "\\frame_bottom.png")
    image_aspect_ratio = bottomborder_image_original.height / bottomborder_image_original.width
    target_border_width = int(hor_border_height / image_aspect_ratio)
    bottomborder_image = ImageTk.PhotoImage(bottomborder_image_original.resize((target_border_width, hor_border_height), Image.ANTIALIAS).crop((0,0,self._right_menu_canvas.winfo_width() + scrollbar.winfo_width(), hor_border_height)))

    bottom_decoration_width = self._GetActualPixelSize(self._right_menu_canvas.winfo_width() + scrollbar.winfo_width())
    bottom_decoration_image = self._GetFullHDFixedWidthPhotoImage(f"{self._skin_path}\\right_menu_bottom.png", bottom_decoration_width)

    bottom_border_frame = ctk.CTkFrame(right_menu_parent_frame, width=0, height=0)
    bottom_decoration_image_label = ctk.CTkLabel(bottom_border_frame, image=bottom_decoration_image, text="")
    bottom_decoration_image_label.pack(fill=tk.X)
    bottom_border_image_label = ctk.CTkLabel(bottom_border_frame, image=bottomborder_image, text="")
    bottom_border_image_label.pack(fill=tk.X)
    bottom_border_frame.pack(fill=tk.X)

def RightMenuResizer(self):
    parent = self._right_menu_parent_frame
    scrolling_canvas = self._right_menu_canvas
    child_scrolling_frame = self._imagebar_thumbnails_frame
    clearance = self._GetScaledPixelSize(self._GetFullHDActualPixelWidthEquivalent(150)) # Menu's minimum clearance from the bottom of the window
    minimum_height = 100 # Menu's minimum height in scaled (not real) pixels. Won't resize smaller than this.
    
    ####### MOVING PART ########
    window_width = self._app.winfo_width()
    
    # Calculate the distance between the left menu and the right menu
    centerdistance = (window_width - parent.winfo_width()) - (self._TTI_main_frame.winfo_x() + self._TTI_main_frame.winfo_width())
    
    # Only move freely if there is enough space for the image at the center, otherwise move just enough to leave space for the image
    #if (centerdistance > self._imagebar_min_width):
    parent.place(x=window_width, anchor="ne")
    #else:
        #self._right_menu_canvas.place(x=(self._TTI_main_frame.winfo_x() + self._TTI_main_frame.winfo_width()) + self._imagebar_min_width, anchor="nw")
    
    ######## RESIZING PART ########
    # Calculate the target height (never smaller than minimum_height)
    target_height = max(minimum_height, self._app.winfo_height() - parent.winfo_y() - clearance)

    # Get the direct child frames of _left_menu_parent_frame
    child_frames = [parent.nametowidget(child_name) for child_name in parent.winfo_children() if (isinstance(parent.nametowidget(child_name), tk.Frame) or isinstance(parent.nametowidget(child_name), ctk.CTkFrame))]

    # Iterate through the direct child frames of _right_menu_parent_frame. Since only the scrollable frame will need to be resized,
    # we remove the size of all other fixed frames from the scrollable frame's target height
    for frame in child_frames:
        if not hasattr(frame, "scrollable"):
            target_height -= frame.winfo_height()

    # If the imagebar thumbnail section is smaller than the target height, then adopt the size of imagebar thumbnail section
    if (child_scrolling_frame.winfo_height()<target_height):
        scrolling_canvas.configure(height=child_scrolling_frame.winfo_height())
    else:
        scrolling_canvas.configure(height=target_height)