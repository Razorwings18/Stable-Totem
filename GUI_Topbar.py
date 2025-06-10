from PIL import ImageTk, Image
import tkinter as tk
import customtkinter as ctk 
import GUIstyles as gs

def BuildTopBar(self):
    """
    Build the top navigation bar. Populates the following globals:\n
    self._top_bar_left_image\n
    self._top_bar_right_image\n
    self._top_bar_center_image\n
    These contain the IDs of those images in self._main_canvas
    """
    # Put the left end
    left_end_image = self._GetFullHDFixedWidthPhotoImage(f"{self._skin_path}\\topbar\\topbar_left.png", 343)
    left_end_leftborder_pos = self._GetScaledPixelSize(self._GetFullHDActualPixelWidthEquivalent(5))
    self._top_bar_left_image = self._main_canvas.create_image(left_end_leftborder_pos, self._GetScaledPixelSize(11), image=left_end_image, anchor="nw")
    self._preservedImages[self._top_bar_left_image] = left_end_image # Store here to avoid the image being garbage-collected
    
    # Put the right end
    right_end_image = self._GetFullHDFixedWidthPhotoImage(f"{self._skin_path}\\topbar\\topbar_right.png", 343)
    right_end_rightborder_pos = self._main_canvas.winfo_width() - self._GetScaledPixelSize(self._GetFullHDActualPixelWidthEquivalent(5))
    self._top_bar_right_image = self._main_canvas.create_image(right_end_rightborder_pos, self._GetScaledPixelSize(11), image=right_end_image, anchor="ne")
    self._preservedImages[self._top_bar_right_image] = right_end_image # Store here to avoid the image being garbage-collected
    
    # Put the center part linking both ends
    center_image_source = Image.open(f"{self._skin_path}\\topbar\\topbar_center.png")
    self._top_bar_center_image_source = center_image_source
    # The center image always has the same height as the left end image. This is a requirement for the skin's images.
    center_image_height = left_end_image.height()
    # Resize the image to fit exactly the space between the left and right ends
    rightX1, *_ = self._main_canvas.bbox(self._top_bar_right_image)
    _, leftY1, leftX2, _ = self._main_canvas.bbox(self._top_bar_left_image)
    center_image_width = (rightX1 - leftX2)
    center_image = ImageTk.PhotoImage(center_image_source.resize((center_image_width, center_image_height), Image.ANTIALIAS))
    # Finally, place the image between both ends
    self._top_bar_center_image = self._main_canvas.create_image(leftX2, leftY1, image=center_image, anchor="nw")
    self._preservedImages[self._top_bar_center_image] = center_image # Store here to avoid the image being garbage-collected

    # Now build the topbar menu
    BuildTopBarMenu(self)

def BuildTopBarMenu(TotemGUI_instance):
    # Since we can't import TotemGUI due to circular reference, make a "mini-cast" here
    from GUI import TotemGUI
    self:TotemGUI = TotemGUI_instance

    # Load bounding box coordinates for the center bar. Our menu will "take place" inside this bounding box.
    centerbar_x1, centerbar_y1, centerbar_x2, centerbar_y2 = self._main_canvas.bbox(self._top_bar_center_image)
    
    # Place the buttons
    navigation_selectbutton = gs.topbar_selectbutton(self._main_canvas, "TEXT TO IMAGE", ["TEXT TO IMAGE", "IMAGE TO IMAGE", "UPSCALE"])
    self._main_canvas.create_window(centerbar_x1, centerbar_y1 + ((centerbar_y2-centerbar_y1)//2), window=navigation_selectbutton, anchor="w")
    
    settings_button = gs.topbar_navigation_button(self._main_canvas, text="SETTINGS", command=self._Settings.DisplaySettingsGUI)
    self._main_canvas.create_window(centerbar_x2, centerbar_y1 + ((centerbar_y2-centerbar_y1)//2), window=settings_button, anchor="e")

def topbar_resizer(self, window_width):
    """
    Called whenever the main window resizes.\n
    Resizes the top bar and makes sure that it never shrinks smaller than its minimum width
    """
    # Make sure everything in the canvas is updated so we don't get erroneous data below
    self._main_canvas.update()

    # Calculate the minimum width the top bar could ever have
    leftX1, leftY1, leftX2, leftY2 = self._main_canvas.bbox(self._top_bar_left_image)
    rightX1, rightY1, rightX2, _ = self._main_canvas.bbox(self._top_bar_right_image)
    minwidth = leftX2 + (rightX2 - rightX1)
    
    if (window_width > minwidth):
        # The window's width is larger than the minimum width. Resize the top bar accordingly.
        new_rightX = self._main_canvas.winfo_width() - self._GetScaledPixelSize(self._GetFullHDActualPixelWidthEquivalent(5))
        self._main_canvas.coords(self._top_bar_right_image, new_rightX, rightY1)
        
        # Get the new rightX1 based on the new position of the right end
        rightX1, *_ = self._main_canvas.bbox(self._top_bar_right_image)
        
        # Build a new central image that fits exactly in the space between the left and right ends as per their new positions
        center_image_width = max((rightX1 - leftX2), 1)
        center_image_height = (leftY2 - leftY1)
        center_image = ImageTk.PhotoImage(self._top_bar_center_image_source.resize((center_image_width, center_image_height), Image.ANTIALIAS))
        
        # Replace the previous image with the new image in _preservedImages so that the last image will hopefully be destroyed by the Garbage Collector
        self._preservedImages[self._top_bar_center_image] = center_image
        # And now place the newly resized image in its place
        self._main_canvas.itemconfigure(self._top_bar_center_image, image=center_image)