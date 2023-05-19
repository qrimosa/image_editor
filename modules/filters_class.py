import time
import tkinter as tk
import customtkinter as ctk
from tkinter import colorchooser
from tkinter import messagebox
from tkinter import filedialog
from PIL import ImageTk, Image
import PIL
import imagehash
from PIL import ImageDraw
from PIL import ImageEnhance
from PIL import ImageFilter
from PIL import ImageFont
from PIL.ExifTags import TAGS
import requests

import os
from PIL import ImageOps

class Filters(tk.Toplevel):
    def __init__(self, parent, image_copy, modified_img, image_copy_resized, modified_img_resized):
        super().__init__(parent)

        self.configure(background="grey")
        self.wm_overrideredirect(True)
        self.grab_set()
        self.winfo_parent()
        self.geometry("150x250+1500+100")
        self.filter_ = None

        self.parent = parent

        self.image_copy = image_copy
        self.modified_img = modified_img

        self.image_copy_resized = image_copy_resized
        self.modified_img_resized = modified_img_resized

        background_color1 = 'black'
        foreground_color = 'white'

        f1 = tk.Frame(self, background=background_color1)
        f1.pack(fill="both", expand=True, padx=5, pady=5)

        tk.Label(f1, text="Filters", background="black", foreground="white", font="arial 11 bold").pack(fill="x")

        filters_frame = tk.Frame(f1, background=background_color1)
        filters_frame.pack(fill="both", expand=True)

        buttons_frame = tk.Frame(f1, background="black", pady=0)
        buttons_frame.pack(fill="both", expand=True)

        emboss_b = tk.Button(filters_frame, text="Emboss", font="arial 8 bold", command=lambda: self.filters(emboss_b),
                             foreground=foreground_color, background="black", padx=17, cursor="hand2", bd = 0)
        
        emboss_b.pack(pady=9)

        grey_b = tk.Button(filters_frame, text="Grey", font="arial 8 bold", command=lambda: self.filters(grey_b),
                           foreground=foreground_color, background="black", padx=8, cursor="hand2", bd = 0)
        
        grey_b.pack(pady=9)

        negative_b = tk.Button(filters_frame, text="Negative", font="arial 8 bold",
                               command=lambda: self.filters(negative_b), foreground=foreground_color,
                               background="black", padx=17, cursor="hand2", bd = 0)
        
        negative_b.pack(pady=9)

        blur_b = tk.Button(filters_frame, text="Gaussian Blur", font="arial 8 bold",
                           command=lambda: self.filters(blur_b), foreground=foreground_color,
                           background="black", padx=17, cursor="hand2", bd = 0)
        
        blur_b.pack(pady=9)

        cancel_b = tk.Button(f1, text="Cancel", command=self.cancel, background='black',
                             foreground=foreground_color, font="arial 12 bold", cursor="hand2", bd = 0)
        
        cancel_b.pack(side="left")

        apply_b = tk.Button(f1, text="Apply", command=self.apply, background='black', foreground=foreground_color,
                            font="arial 12 bold", padx=8, cursor="hand2", bd = 0)
        
        apply_b.pack(side="left")

    def filters(self, button):
        self.filter_ = button['text'].lower()

        if self.filter_ == 'emboss':
            self.modified_img = self.image_copy.filter(ImageFilter.EMBOSS)

            self.modified_img_resized = self.image_copy_resized.filter(ImageFilter.EMBOSS)
            im = ImageTk.PhotoImage(self.modified_img_resized)
            self.parent.show_image(modified=im)

        elif self.filter_ == 'negative':
            self.modified_img = ImageOps.invert(self.image_copy)

            self.modified_img_resized = ImageOps.invert(self.image_copy_resized)
            im = ImageTk.PhotoImage(self.modified_img_resized)
            self.parent.show_image(modified=im)

        elif self.filter_ == 'grey':
            self.modified_img = ImageOps.grayscale(self.image_copy)

            self.modified_img_resized = ImageOps.grayscale(self.image_copy_resized)
            im = ImageTk.PhotoImage(self.modified_img_resized)
            self.parent.show_image(modified=im)

        elif self.filter_ == 'gaussian blur':
            self.modified_img = self.image_copy.filter(ImageFilter.GaussianBlur)

            self.modified_img_resized = self.image_copy_resized.filter(ImageFilter.GaussianBlur)
            im = ImageTk.PhotoImage(self.modified_img_resized)
            self.parent.show_image(modified=im)

    def cancel(self):
        self.grab_release()

        im = ImageTk.PhotoImage(self.image_copy_resized)
        self.parent.show_image(modified=im)
        self.destroy()

    def apply(self):
        self.grab_release()

        self.parent.image_copy = self.modified_img

        self.parent.image_copy_resized = self.modified_img_resized
        if self.filter_:
            self.parent.save_bt.configure(state="normal")

        im = ImageTk.PhotoImage(self.parent.image_copy_resized)
        self.parent.show_image(modified=im)
        self.destroy()