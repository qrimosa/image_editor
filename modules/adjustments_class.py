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

class Adjustments(tk.Toplevel):
    def __init__(self, parent, image_copy, modified_img, image_copy_resized, modified_img_resized):
        super().__init__(parent)

        self.parent = parent
        self.configure(background="grey")
        self.wm_overrideredirect(True)
        self.grab_set()
        self.winfo_parent()
        self.geometry("260x280+1400+100")

        self.image_copy = image_copy
        self.modified_img = modified_img

        self.image_copy_resized = image_copy_resized
        self.modified_img_resized = modified_img_resized

        self.modifications = {'contrast': 1.0, 'sharpness': 1.0, 'brightness': 1.0}

        background_color1 = 'black'
        background_color2 = 'black'

        f1 = tk.Frame(self, background=background_color1)
        f1.pack(fill="both", expand=True, padx=5, pady=5)

        tk.Label(f1, text="Adjustments", background="black", foreground="white", font="arial 13 bold").pack(fill="x")

        contrast_l = tk.Label(f1, text="Contrast", relief="solid", font="arial 11 bold", background=background_color2,
                              foreground="white")
        contrast_l.place(x=15, y=60)

        self.contrast_b = tk.Scale(f1, from_=0, to=20, sliderrelief='flat',
                                   command=lambda e: self.adjust(e, 'contrast'),
                                   orient="horizontal", highlightthickness=0, background=background_color1, fg='white',
                                   troughcolor='#73B5FA', activebackground='#1065BF')
        self.contrast_b.place(x=120, y=40)

        sharpness_l = tk.Label(f1, text="Sharpness", font="arial 11 bold", background=background_color2,
                               foreground="white")
        sharpness_l.place(x=15, y=100)

        self.sharpness_b = tk.Scale(f1, from_=0, to=30, sliderrelief='flat',
                                    command=lambda e: self.adjust(e, 'sharpness'),
                                    orient="horizontal", highlightthickness=0, background=background_color1, fg='white',
                                    troughcolor='#73B5FA', activebackground='#1065BF')
        self.sharpness_b.place(x=120, y=80)
        
        brightness_l = tk.Label(f1, text="Brightness", font="Arial 11 bold", background=background_color2,
                                foreground="white")
        brightness_l.place(x=15, y=140)

        self.brightness_b = tk.Scale(f1, from_=0, to=20, sliderrelief='flat',
                                     command=lambda e: self.adjust(e, 'brightness'),
                                     orient="horizontal", highlightthickness=0, background=background_color1,
                                     fg='white',
                                     troughcolor='#73B5FA', activebackground='#1065BF')
        self.brightness_b.place(x=120, y=120)

        cancel_b = tk.Button(f1, text="Cancel", command=self.cancel, relief="solid", background=background_color1,
                             foreground="white", font="arial 12 bold", cursor="hand2")
        cancel_b.place(x=45, y=220)

        apply_b = tk.Button(f1, text="Apply", command=self.apply, relief="solid", background=background_color1,
                            foreground="white",
                            font="arial 12 bold", padx=8, cursor="hand2")
        apply_b.place(x=130, y=220)

    def adjust(self, e, changes):
        im2 = self.image_copy
        im2_resized = self.image_copy_resized

        if 'original_image':
            if self.modifications:
                for modification in self.modifications.copy():

                    if changes == 'sharpness' and modification == 'sharpness':
                        del self.modifications[modification]

                    elif changes == 'contrast' and modification == 'contrast':
                        del self.modifications[modification]

                    elif changes == 'brightness' and modification == 'brightness':
                        del self.modifications[modification]

                    else:
                        property_ = modification
                        value = self.modifications[property_]

                        if property_ == 'sharpness':

                            enhancer = ImageEnhance.Sharpness(im2)
                            self.modified_img = enhancer.enhance(value)

                            enhancer = ImageEnhance.Sharpness(im2_resized)
                            self.modified_img_resized = enhancer.enhance(value)

                            im = ImageTk.PhotoImage(self.modified_img_resized)
                            self.parent.show_image(modified=im)

                            im2 = self.modified_img
                            im2_resized = self.modified_img_resized

                        elif property_ == 'contrast':

                            enhancer = ImageEnhance.Contrast(im2)
                            self.modified_img = enhancer.enhance(value)

                            enhancer = ImageEnhance.Contrast(im2_resized)
                            self.modified_img_resized = enhancer.enhance(value)

                            im = ImageTk.PhotoImage(self.modified_img_resized)
                            self.parent.show_image(modified=im)

                            im2 = self.modified_img
                            im2_resized = self.modified_img_resized

                        elif property_ == 'brightness':

                            enhancer = ImageEnhance.Brightness(im2)
                            self.modified_img = enhancer.enhance(value)

                            enhancer = ImageEnhance.Brightness(im2_resized)
                            self.modified_img_resized = enhancer.enhance(value)

                            im = ImageTk.PhotoImage(self.modified_img_resized)
                            self.parent.show_image(modified=im)

                            im2 = self.modified_img
                            im2_resized = self.modified_img_resized

                if changes == 'sharpness':
                    self.modifications['sharpness'] = int(e) / 10

                    enhancer = ImageEnhance.Sharpness(self.modified_img)
                    self.modified_img = enhancer.enhance(int(e) / 10)

                    enhancer = ImageEnhance.Sharpness(self.modified_img_resized)
                    self.modified_img_resized = enhancer.enhance(int(e) / 10)

                    im = ImageTk.PhotoImage(self.modified_img_resized)
                    self.parent.show_image(modified=im)

                elif changes == 'contrast':
                    self.modifications['contrast'] = int(e) / 10

                    enhancer = ImageEnhance.Contrast(self.modified_img)
                    self.modified_img = enhancer.enhance(int(e) / 10)

                    enhancer = ImageEnhance.Contrast(self.modified_img_resized)
                    self.modified_img_resized = enhancer.enhance(int(e) / 10)

                    im = ImageTk.PhotoImage(self.modified_img_resized)
                    self.parent.show_image(modified=im)

                elif changes == 'brightness':
                    self.modifications['brightness'] = int(e) / 10

                    enhancer = ImageEnhance.Brightness(self.modified_img)
                    self.modified_img = enhancer.enhance(int(e) / 10)

                    enhancer = ImageEnhance.Brightness(self.modified_img_resized)
                    self.modified_img_resized = enhancer.enhance(int(e) / 10)

                    im = ImageTk.PhotoImage(self.modified_img_resized)
                    self.parent.show_image(modified=im)

    def cancel(self):
        self.grab_release()

        im = ImageTk.PhotoImage(self.image_copy_resized)
        self.parent.show_image(modified=im)
        self.destroy()

    def apply(self):
        self.modifications = {'contrast': 1.0, 'sharpness': 1.0, 'brightness': 1.0}
        self.grab_release()

        for i in (self.brightness_b, self.contrast_b, self.sharpness_b):
            if i.get() != 10:
                self.parent.save_bt.configure(state="normal")
                break

        self.parent.image_copy = self.modified_img
        self.parent.image_copy_resized = self.modified_img_resized

        im = ImageTk.PhotoImage(self.parent.image_copy_resized)
        self.parent.show_image(modified=im)
        self.destroy()