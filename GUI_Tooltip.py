import tkinter as tk
import customtkinter as ctk

class Tooltip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tip_window = None
        self.id = None
        self.x = self.y = 0

        widget.bind("<Enter>", self.show_tooltip, add="+")
        widget.bind("<Leave>", self.hide_tooltip, add="+")

    def show_tooltip(self, event):
        self.x = event.x_root + 10
        self.y = event.y_root + 10

        self.tip_window = tk.Toplevel(self.widget)
        self.tip_window.wm_overrideredirect(True)
        self.tip_window.wm_geometry("+%d+%d" % (self.x, self.y))

        label = ctk.CTkLabel(self.tip_window, text=self.text, fg_color="#977b58", text_color="white", font=("Arial", 10), 
                             bg_color="black", corner_radius=0)
        label.pack()

    def hide_tooltip(self, _):
        if self.tip_window:
            self.tip_window.destroy()