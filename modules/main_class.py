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
import modules.filters_class as filters
import modules.adjustments_class as adjustments

import os
from PIL import ImageOps

class ImageEditor(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        window_width, window_height = 500, 500
        screen_width, screen_height = self.winfo_screenwidth(), self.winfo_screenheight()
        x_co, y_co = 500, 500 
        self.geometry(f"{window_width}x{window_height}+{x_co}+{y_co}")
        self.state("zoomed")
        self.title("Image Editor")
        self.config(bg = "#000000")
        self.wm_iconbitmap('icons/icon.ico')
        
        self.button_background = 'grey'
        self.original_image_resized = None
        self.image_copy_resized = None
        self.modified_img_resized = None
        self.image_before_draw = None
        self.draw_active = False
        self.crop_active = False
        self.text_active = False #new
        self.text_written = False #new
        self.download_active = False
        self.mirrored = False
        self.current_index = None
        self.image_paths = []
        self.lines_drawn = []
        self.current_image_size = None
        self.current_resized_image_size = None
        self.original_image = None
        self.modified_img = None
        self.image_copy = None
        self.rect = None
        self.event_x = self.event_y = None  
        self.rectangles = []
        self.point_x = self.point_y = None
        self.image_x_co = self.image_y_co = None
        self.original_hash = None

        self.max_height = 812
        self.max_width = 1220

        self.degree = 90

        flip_icon = Image.open('icons/flip2_ie.png')
        flip_icon = flip_icon.resize((35, 35), Image.LANCZOS)
        flip_icon = ImageTk.PhotoImage(flip_icon)

        rotate_icon = Image.open('icons/rotate_ie.png')
        rotate_icon = rotate_icon.resize((35, 35), Image.LANCZOS)
        rotate_icon = ImageTk.PhotoImage(rotate_icon)

        next_icon = Image.open('icons/right_ie.png')
        next_icon = next_icon.resize((35, 35), Image.LANCZOS)
        next_icon = ImageTk.PhotoImage(next_icon)

        previous_icon = Image.open('icons/left_ie.png')
        previous_icon = previous_icon.resize((35, 35), Image.LANCZOS)
        previous_icon = ImageTk.PhotoImage(previous_icon)

        adjust_icon = Image.open('icons/adjust_ie.png')
        adjust_icon = adjust_icon.resize((25, 25), Image.LANCZOS)
        adjust_icon = ImageTk.PhotoImage(adjust_icon)

        filter_icon = Image.open('icons/filter_ie.png')
        filter_icon = filter_icon.resize((25, 25), Image.LANCZOS)
        filter_icon = ImageTk.PhotoImage(filter_icon)

        save_icon = Image.open('icons/save_ie.png')
        save_icon = save_icon.resize((25, 25), Image.LANCZOS)
        save_icon = ImageTk.PhotoImage(save_icon)

        power_off_icon = Image.open('icons/power-button_ie.png')
        power_off_icon = power_off_icon.resize((25, 25), Image.LANCZOS)
        power_off_icon = ImageTk.PhotoImage(power_off_icon)

        self.open_image_icon = Image.open('icons/open_image_ie.png')
        self.open_image_icon = self.open_image_icon.resize((150, 120), Image.LANCZOS)
        self.open_image_icon = ImageTk.PhotoImage(self.open_image_icon)

        self.open_image_small_icon = Image.open('icons/open_image_ie.png')
        self.open_image_small_icon = self.open_image_small_icon.resize((50, 40), Image.LANCZOS)
        self.open_image_small_icon = ImageTk.PhotoImage(self.open_image_small_icon)

        self.checked_icon = Image.open('icons/checked_ie.png')
        self.checked_icon = self.checked_icon.resize((25, 25), Image.LANCZOS)
        self.checked_icon = ImageTk.PhotoImage(self.checked_icon)

        self.unchecked_icon = Image.open('icons/unchecked_ie.png')
        self.unchecked_icon = self.unchecked_icon.resize((25, 25), Image.LANCZOS)
        self.unchecked_icon = ImageTk.PhotoImage(self.unchecked_icon)

        reset_icon = Image.open('icons/reset_ie.png')
        reset_icon = reset_icon.resize((25, 25), Image.LANCZOS)
        reset_icon = ImageTk.PhotoImage(reset_icon)

        color_picker_icon = Image.open('icons/color_picker_ie.png')
        color_picker_icon = color_picker_icon.resize((25, 25), Image.LANCZOS)
        color_picker_icon = ImageTk.PhotoImage(color_picker_icon)

        self.image_canvas = tk.Canvas(self, bd=0, highlightbackground="black", background="black")
        self.image_canvas.bind('<B1-Motion>', self.draw_crop)
        self.image_canvas.bind('<ButtonPress-1>', self.get_mouse_pos)
        self.image_canvas.bind('<ButtonRelease-1>', self.button_release)
        self.image_canvas.pack(fill="both", expand=True)

        self.button_frame_color = "black"

        previous_bt = tk.Button(self, text = "Previous", command = self.previous_image, width = 30, height = 30, image = previous_icon, background= self.button_frame_color, cursor="hand2", bd = 0)
        previous_bt.place(x = screen_width // 2 - 50 * 2, y = screen_height - 100)

        rotate_bt = tk.Button(self, text = "Rotate", command = self.rotate, width = 30, height = 30, image = rotate_icon, background= self.button_frame_color, cursor="hand2", bd = 0)
        rotate_bt.place(x = screen_width // 2 - 50, y = screen_height - 100)

        flip_bt = tk.Button(self, text = "Flip", command = self.mirror, width = 30, height = 30, image = flip_icon, background= self.button_frame_color, cursor="hand2", bd = 0)
        flip_bt.place(x = screen_width // 2 , y = screen_height - 100)

        next_bt = tk.Button(self, text = "Next", command = self.next_image, width = 30, height = 30, image = next_icon, background= self.button_frame_color, cursor="hand2", bd = 0)
        next_bt.place(x = screen_width // 2 + 50, y = screen_height - 100)

        self.adjust_bt = tk.Button(self, text="Adjust", width = 80, height = 30, foreground="white", compound="left", font="Arial 12 bold",
                             image=adjust_icon, background="black", cursor="hand2", bd = 0, command = self.open_adjustment_window)
        
        self.filter_bt = tk.Button(self, text="Filters", width = 80, height = 30, foreground="white", compound="left", font="Arial 12 bold",
                             image=filter_icon, background="black", cursor="hand2", bd = 0, command = self.open_filter_window)
        
        self.reset_bt = tk.Button(self, text="Reset", width = 80, height = 30, foreground="white", compound="left", font="Arial 12 bold",
                             image=reset_icon, background="black", cursor="hand2", bd = 0, command = self.reset)
        
        self.crop_bt = tk.Button(self, text="Crop", width = 80, height = 30, foreground="white", compound="left", font="Arial 12 bold",
                             image=self.unchecked_icon, background="black", cursor="hand2", bd = 0, command = self.activate_crop)
        
        self.save_crop_bt = tk.Button(self, text="Save", width = 80, height = 30, foreground="white", compound="left", font="Arial 12 bold",
                             image=save_icon, background="black", cursor="hand2", bd = 0, command= self.crop_image)
        
        self.draw_bt = tk.Button(self, text="Draw", width = 80, height = 30, foreground="white", compound="left", font="Arial 12 bold",
                             image=self.unchecked_icon, background="black", cursor="hand2", bd = 0, command = self.activate_draw)
        
        self.save_draw_bt = tk.Button(self, text="Save", width = 80, height = 30, foreground="white", compound="left", font="Arial 12 bold",
                             image=save_icon, background="black", cursor="hand2", bd = 0, command = self.image_after_draw)

        self.save_bt = tk.Button(self, text="Save", foreground="white", compound="left",
                                font="Arial 12 bold", state='disabled', image=save_icon, background="black", cursor="hand2", bd = 0, command= self.save)
        
        self.text_bt = tk.Button(self, text="Text", foreground="white", compound="left",
                                font="Arial 12 bold", image=self.unchecked_icon, background="black", cursor="hand2", bd = 0, command = self.activate_text)
        
        self.save_text_bt = tk.Button(self, text="Save", width = 80, height = 30, foreground="white", compound="left", font="Arial 12 bold",
                             image=save_icon, background="black", cursor="hand2", bd = 0, command = self.image_after_text) 

        self.text_entry = tk.Entry(self, font = "Arial 12 bold", cursor="xterm")

        self.add_text_bt = tk.Button(self, text="Add Text", foreground="white", 
                                font="Arial 12 bold", background="black", cursor="hand2", bd = 0, command = self.add_text)

        self.status_bar = tk.Label(self, background=self.button_frame_color,
                                   foreground="white", font="lucida 10 bold")
        self.status_bar.place(x=1500, y = 900)

        self.open_image_button = tk.Button(self, cursor="hand2",
                                           image=self.open_image_icon, command = self.open_image, compound='top', text="Click To Open Image",
                                           font="Arial 15 bold", foreground="white", bd=0, background="black")
        self.open_image_button.place(x=685, y=350)

        self.download_image_button = tk.Button(self, cursor="hand2",
                                           image=self.open_image_small_icon, compound='top', text="Download Image via URL",
                                           font="Arial 12 bold", foreground="white", bd=0, background="black", command = self.activate_download)
        
        self.url_entry = tk.Entry(self, font = "Arial 12 bold", cursor="xterm")

        self.listbox = tk.Listbox(self, width = 25, height = 15, bg = "black", fg = "white", font= "arial 14 bold")
        
        self.download_bt = tk.Button(self, text="Download", foreground="white", 
                                font="Arial 12 bold", background="black", cursor="hand2", bd = 0, command = self.download_image)

        self.info_label = tk.Label(self, text= "", background = "black", foreground="white", font = "arial 15 bold")
        self.info_label.place(x = 100, y = 600)

        self.pencil_size = 2
        self.pencil_color = 'red'

        self.pencil_size_label = tk.Label(self, text="Size", font="arial 10 bold",
                                          background='black', foreground="white")

        self.pencil_size_scale = tk.Scale(self, from_=1, to=15, sliderrelief='flat',
                                          orient="horizontal", fg='white', highlightthickness=0, cursor="hand2", background='black',
                                          troughcolor='#73B5FA', activebackground='#1065BF', command = self.change_pencil_size)    

        self.color_chooser_button = tk.Button(self, image=color_picker_icon, text="Color",
                                              font="lucida 10 bold", cursor="hand2", background='black',
                                              foreground="white", bd=0, command= self.choose_color)
        
        
        self.mainloop()

    def change_pencil_size(self, size):
        self.pencil_size = int(size)

    def choose_color(self):
        color = colorchooser.askcolor(initialcolor='red')
        if color[0]:
            self.pencil_color = color[1]

    def open_image(self):
        file_object = filedialog.askopenfile(filetype=(('jpg', '*.jpg'), ('png', '*.png')))
        if file_object:

            self.open_image_button.configure(image=self.open_image_small_icon, text="Open Image", compound="top",
                                             font="arial 12 bold")
            self.open_image_button.place(x = 1920 - 200, y = 700)
            
            self.adjust_bt.place(x = 1920 - 200, y = 250)
            self.filter_bt.place(x = 1920 - 200, y = 300)
            self.save_bt.place(x = 1920 - 200, y = 600)
            self.draw_bt.place(x = 1920 - 250, y = 200)
            self.crop_bt.place(x = 1920 - 150, y = 200)
            self.reset_bt.place(x = 1920 - 200, y = 350)
            self.text_bt.place(x = 1920 - 200, y = 150)
            self.listbox.place(x = 85, y = 200)
            self.download_image_button.place(x = 1920 - 250, y = 800)

            filename = file_object.name
            directory = filename.replace(os.path.basename(filename), "")
            files_list = os.listdir(directory)

            self.image_paths = []
            for file in files_list:
                if '.jpg' in file or '.png' in file or '.JPG' in file or '.JPEG' in file or '.PNG' in file:
                    self.image_paths.append(os.path.join(directory, file))

            for file in files_list:
                if '.jpg' in file or '.png' in file or '.JPG' in file or '.JPEG' in file or '.PNG' in file:
                    self.listbox.insert('end', file)
            
            for i, image in enumerate(self.image_paths):
                if image == filename:
                    self.current_index = i
            self.show_image(image=self.image_paths[self.current_index])

    def activate_download(self):
        if not self.download_active:
            self.download_bt.place(x = 1920 - 200, y = 300)
            self.url_entry.place(x = 1920 - 250, y = 250)

            self.open_image_button.place_forget()
            self.crop_bt.place_forget()
            self.save_bt.place_forget()
            self.adjust_bt.place_forget()
            self.reset_bt.place_forget()
            self.filter_bt.place_forget()
            self.text_bt.place_forget()
            self.draw_bt.place_forget()
            self.download_active = True
        else:
            self.save_bt.place(x = 1920 - 200, y = 600)
            self.crop_bt.place(x = 1920 - 150, y = 200)
            self.adjust_bt.place(x = 1920 - 200, y = 250)
            self.filter_bt.place(x = 1920 - 200, y = 300)
            self.reset_bt.place(x = 1920 - 200, y = 350)
            self.text_bt.place(x = 1920 - 200, y = 150)
            self.draw_bt.place(x = 1920 - 250, y = 200)
            self.open_image_button.place(x = 1920 - 200, y = 700)

            self.download_bt.place_forget()
            self.url_entry.place_forget()
            self.download_active = False

    def download_image(self):
        self.url = self.url_entry.get()
        data = requests.get(self.url).content
        f = open('img.jpg','wb')
        f.write(data)
        f.close()
        self.url_entry.delete(0, 'end')

    def resize_image(self, image):
        image.thumbnail((self.max_width, self.max_height))

        self.original_hash = imagehash.average_hash(image)

        self.current_resized_image_size = (image.size[0], image.size[1])
        return image

    def photo_image_object(self, image):
        self.original_image = Image.open(image)
        self.current_image_size = self.original_image.size
        self.modified_img = self.original_image
        self.image_copy = self.original_image

        self.original_image_resized = Image.open(image)
        width, height = self.original_image_resized.size
        self.info_label.configure(text = "Size: " + str(os.stat(self.image_paths[self.current_index]).st_size / 1000000) + " MB" + "\nWidth: " + str(width)+ "\nHeight: " + str(height))
        
        self.modified_img_resized = self.original_image_resized
        self.image_copy_resized = self.original_image_resized

        im = self.resize_image(self.original_image_resized)
        im = ImageTk.PhotoImage(im)
        return im

    def show_image(self, image=None, modified=None):
        self.status_bar.configure(text=f"Image:  {self.current_index + 1}  of  {len(self.image_paths)}")
        im = None
        if image:
            try:
                im = self.photo_image_object(image)
            except:
                self.image_copy = self.modified_img = self.original_image_resized = self.original_image = None
                self.image_canvas.image = ''
                return

        elif modified:
            im = modified

        image_width, image_height = self.current_resized_image_size[0], self.current_resized_image_size[1]
        self.image_x_co, self.image_y_co = (self.winfo_screenwidth() / 2) - image_width / 2, (
                self.max_height / 2) - image_height / 2
        self.image_canvas.image = im

        if image_height < self.max_height:
            self.image_canvas.create_image(self.image_x_co, self.image_y_co, image=im, anchor="nw")
        else:
            self.image_canvas.create_image(self.image_x_co, 0, image=im, anchor="nw")

    def previous_image(self):
        if self.image_paths:
            self.save_bt.configure(state="disable")

            if self.current_index != 0:
                self.current_index -= 1
            self.show_image(image=self.image_paths[self.current_index])


    def next_image(self):
        if self.image_paths:
            self.save_bt.configure(state="disable")

            if self.current_index != len(self.image_paths) - 1:
                self.current_index += 1
            self.show_image(image=self.image_paths[self.current_index])


    def rotate(self):
        if self.original_image:
            self.modified_img_resized = self.image_copy_resized.rotate(-self.degree, expand=True)
            self.image_copy_resized = self.modified_img_resized

            self.modified_img = self.image_copy.rotate(-self.degree, expand=True)

            self.image_copy = self.modified_img
            self.image_copy_resized = self.modified_img_resized

            self.compare_images()

            self.current_resized_image_size = self.modified_img_resized.size

            im = ImageTk.PhotoImage(self.modified_img_resized)
            self.show_image(modified=im)

    def mirror(self):
        if self.original_image:
            if not self.mirrored:
                self.modified_img = self.image_copy.transpose(PIL.Image.FLIP_LEFT_RIGHT)
                self.modified_img_resized = self.image_copy_resized.transpose(PIL.Image.FLIP_LEFT_RIGHT)
                self.mirrored = True
            else:
                self.modified_img = self.modified_img.transpose(PIL.Image.FLIP_LEFT_RIGHT)
                self.modified_img_resized = self.modified_img_resized.transpose(PIL.Image.FLIP_LEFT_RIGHT)
                self.mirrored = False

            self.image_copy = self.modified_img
            self.image_copy_resized = self.modified_img_resized

            self.compare_images()

            im = ImageTk.PhotoImage(self.modified_img_resized)
            self.show_image(modified=im)

    def get_mouse_pos(self, event):
        if not self.draw_active and self.crop_active:
            if self.rect:
                self.rectangles = []
                self.image_canvas.delete(self.rect)

            self.rect = self.image_canvas.create_rectangle(0, 0, 0, 0, outline="black", width=3)

        self.point_x, self.point_y = event.x, event.y

    def button_release(self, event):
        if self.crop_active:
            self.save_crop_bt.place(x=1920 - 250, y = 200)

    def activate_draw(self):
        if self.original_image:
            if not self.draw_active:
                
                self.image_before_draw = Image.new('RGB', size=self.current_image_size)
                self.image_before_draw.paste(self.image_copy, (0, 0))

                self.pencil_size_label.place(x = 1920 - 250, y = 275)
                self.pencil_size_scale.place(x = 1920 - 200, y = 260)
                self.color_chooser_button.place(x = 1920 - 200, y = 320)

                self.image_canvas.configure(cursor='pencil')
                self.save_draw_bt.place(x = 1920 - 150, y = 200)

                self.draw_bt.configure(image=self.checked_icon)
                self.crop_bt.place_forget()
                self.save_bt.place_forget()
                self.adjust_bt.place_forget()
                self.reset_bt.place_forget()
                self.filter_bt.place_forget()
                self.text_bt.place_forget()

                self.draw_active = True
            else:
                if self.lines_drawn:
                    for line in self.lines_drawn:
                        self.image_canvas.delete(line)
                    self.lines_drawn = []
                    self.image_before_draw = None
                    self.image_before_draw = self.image_copy

                self.image_canvas.configure(cursor='arrow')
                self.draw_bt.configure(image=self.unchecked_icon)
                self.draw_active = False

                self.save_bt.place(x = 1920 - 200, y = 600)
                self.crop_bt.place(x = 1920 - 150, y = 200)
                self.adjust_bt.place(x = 1920 - 200, y = 250)
                self.filter_bt.place(x = 1920 - 200, y = 300)
                self.reset_bt.place(x = 1920 - 200, y = 350)
                self.text_bt.place(x = 1920 - 200, y = 150)

                self.pencil_size_label.place_forget()
                self.pencil_size_scale.place_forget()
                self.color_chooser_button.place_forget()
                self.save_draw_bt.place_forget()

    def activate_text(self):
        if self.original_image:
            if not self.text_active:
                
                self.text_entry.place(x = 1920 - 250, y = 200)
                self.add_text_bt.place(x = 1920 - 200, y = 250)
                self.save_text_bt.place(x = 1920 - 210, y = 100)

                self.text_bt.configure(image = self.checked_icon)
                self.text_active = True
                self.crop_bt.place_forget()
                self.save_bt.place_forget()
                self.adjust_bt.place_forget()
                self.reset_bt.place_forget()
                self.filter_bt.place_forget()
                self.draw_bt.place_forget()

            else:
                self.text_bt.configure(image=self.unchecked_icon)
                self.save_crop_bt.place_forget()

                self.text_active = False
                self.save_bt.place(x = 1920 - 200, y = 600)
                self.draw_bt.place(x = 1920 - 250, y = 200)
                self.crop_bt.place(x = 1920 - 150, y = 200)
                self.reset_bt.place(x = 1920 - 200, y = 350)
                self.adjust_bt.place(x = 1920 - 200, y = 250)
                self.filter_bt.place(x = 1920 - 200, y = 300)

                self.text_entry.place_forget()
                self.add_text_bt.place_forget()
                self.save_text_bt.place_forget()

    def add_text(self):
        if self.text_active:
            
            self.text_to_add = self.text_entry.get()
            self.text_font = ImageFont.truetype("arial.ttf", 35)
            edit_image = ImageDraw.Draw(self.image_copy)
            edit_image.text((100, 100), self.text_to_add, ("black"), font = self.text_font)
            self.text_entry.delete(0, 'end')
            self.text_written = True

    def image_after_text(self):
        if self.text_written:
            self.save()
        else:
            messagebox.showinfo(title='Cannot save!', message='You have not drawn added the text to the image.')

    def activate_crop(self):
        if self.original_image:
            if self.draw_active:
                self.activate_draw()

            if not self.crop_active:
                self.crop_bt.configure(image=self.checked_icon)
                self.image_canvas.configure(cursor='plus')
                self.crop_active = True
                self.reset_bt.place_forget()
                self.draw_bt.place_forget()
                self.save_bt.place_forget()
                self.adjust_bt.place_forget()
                self.filter_bt.place_forget()
                self.text_bt.place_forget()

            else:
                self.image_canvas.configure(cursor='arrow')
                self.crop_bt.configure(image=self.unchecked_icon)
                self.save_crop_bt.place_forget()
                if self.rect:
                    self.image_canvas.delete(self.rect)

                self.crop_active = False
                self.save_bt.place(x = 1920 - 200, y = 600)
                self.draw_bt.place(x = 1920 - 250, y = 200)
                self.crop_bt.place(x = 1920 - 150, y = 200)
                self.reset_bt.place(x = 1920 - 200, y = 350)
                self.adjust_bt.place(x = 1920 - 200, y = 250)
                self.filter_bt.place(x = 1920 - 200, y = 300)
                self.text_bt.place(x = 1920 - 200, y = 150)
    
    def draw_crop(self, event):
        if self.crop_active:
            if not self.rectangles:
                self.rectangles.append(self.rect)

            image_width, image_height = self.current_resized_image_size[0], self.current_resized_image_size[1]
            x_co_1, x_co_2 = int((self.winfo_screenwidth() / 2) - image_width / 2), int(
                (self.winfo_screenwidth() / 2) + image_width / 2)
            y_co_1, y_co_2 = int(self.max_height / 2 - image_height / 2), int((self.max_height / 2) + image_height / 2)

            if x_co_2 > event.x > x_co_1 and y_co_1 + 2 < event.y < y_co_2:
                self.image_canvas.coords(self.rect, self.point_x, self.point_y, event.x, event.y)

                self.event_x, self.event_y = event.x, event.y

        elif self.draw_active:
            image_width, image_height = self.current_resized_image_size[0], self.current_resized_image_size[1]
            x_co_1, x_co_2 = int((self.winfo_screenwidth() / 2) - image_width / 2), int(
                (self.winfo_screenwidth() / 2) + image_width / 2)
            y_co_1, y_co_2 = int(self.max_height / 2 - image_height / 2), int((self.max_height / 2) + image_height / 2)

            if x_co_2 > self.point_x > x_co_1 and y_co_1 < self.point_y < y_co_2:
                if x_co_2 > event.x > x_co_1 and y_co_1 < event.y < y_co_2:
                    lines = self.image_canvas.create_line(self.point_x, self.point_y, event.x, event.y,
                                                          fill=self.pencil_color, width=self.pencil_size)

                    x_co_1, y_co_1, x_co_2, y_co2 = ((self.point_x - self.image_x_co) * self.current_image_size[0])/self.current_resized_image_size[0], ((self.point_y - self.image_y_co)*self.current_image_size[1])/self.current_resized_image_size[1], ((event.x - self.image_x_co)*self.current_image_size[0])/self.current_resized_image_size[0], ((event.y - self.image_y_co)*self.current_image_size[1])/self.current_resized_image_size[1]

                    img = ImageDraw.Draw(self.image_before_draw)
                    img.line([(x_co_1, y_co_1), (x_co_2, y_co2)], fill=self.pencil_color, width=self.pencil_size + 1)

                    self.lines_drawn.append(lines)
                    self.point_x, self.point_y = event.x, event.y
    
    def crop_image(self):
        if self.rectangles:
            x_co_1, y_co_1, x_co_2, y_co2 = ((self.point_x - self.image_x_co) * self.current_image_size[0])/self.current_resized_image_size[0], ((self.point_y - self.image_y_co) * self.current_image_size[1]) / self.current_resized_image_size[1], ((self.event_x - self.image_x_co) * self.current_image_size[0]) / self.current_resized_image_size[0], ((self.event_y - self.image_y_co) * self.current_image_size[1]) / self.current_resized_image_size[1]

            self.image_copy = self.image_copy.crop((int(x_co_1), int(y_co_1), int(x_co_2), int(y_co2)))
            x_co_1, y_co_1, x_co_2, y_co2 = self.point_x - self.image_x_co, self.point_y - self.image_y_co, self.event_x - self.image_x_co, self.event_y - self.image_y_co

            self.save()
        else:
            messagebox.showinfo(title="Can't crop !", message="Please select the portion of the image,"
                                                              " you want to crop")
            
    def image_after_draw(self):
        if self.lines_drawn:
            self.image_copy = self.image_before_draw
            self.save()
        else:
            messagebox.showinfo(title='Cannot save!', message='You have not drawn anything on the image.')

    def save(self):
        image_path_object = filedialog.asksaveasfile(defaultextension='.jpg')

        if image_path_object:
            image_path = image_path_object.name
            if self.draw_active:
                for line in self.lines_drawn:
                    self.image_canvas.delete(line)
                self.lines_drawn = []

                self.activate_draw()

            if self.crop_active:
                self.image_canvas.delete(self.rect)

                self.activate_crop()

            self.image_copy.save(image_path)
            self.image_paths.insert(self.current_index + 1, image_path)
            self.current_index += 1
            self.show_image(image=image_path)

        self.save_bt.configure(state="disable")
    
    def reset(self):
        if self.original_image:
            if self.draw_active:
                for line in self.lines_drawn:
                    self.image_canvas.delete(line)
                    self.lines_drawn = []
                self.image_before_draw = self.image_copy
            else:
                current_original_image = self.image_paths[self.current_index]
                self.show_image(image=current_original_image)

            self.save_bt.configure(state="disable")

    def open_adjustment_window(self):
        if self.original_image:
            adjustments.Adjustments(self, self.image_copy, self.modified_img, self.image_copy_resized, self.modified_img_resized)

    def open_filter_window(self):
        if self.original_image:
            filters.Filters(self, self.image_copy, self.modified_img, self.image_copy_resized, self.modified_img_resized)
    
    def compare_images(self):   
        if self.original_hash != imagehash.average_hash(self.image_copy_resized):
            self.save_bt.configure(state="normal")
        else:
            self.save_bt.configure(state='disable')

def mouse_not_hover(button, color=None):
    if not color:   
        color = 'black'
    button.configure(bg=color)


def mouse_hover(button, color=None):
    if not color:
        color = '#473f3f'
    button.configure(bg=color)