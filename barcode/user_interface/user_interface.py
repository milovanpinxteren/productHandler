import tkinter as tk
from tkinter import Label, Entry, Button, LEFT
import cv2
from PIL import Image, ImageTk
import datetime
import os

class UserInterface:
    def __init__(self):
        self.root = tk.Tk()
        self.root.geometry("1050x700")
        self.root.title("Product Information Entry")
        self.initialize_widgets()

    def initialize_widgets(self):
        self.info_label = Label(self.root, text="Flow: 1. Scan barcode, en haal Untappd gegevens op. 2. Vul de titel in (na de suggestie van Untappd) 3. Maak foto's en verstuur deze naar Shopify. 4. Controleer of de url van de foto's zijn toegevoegd. 5. Vul de missende gegevens in en druk op Verzenden naar Shopify", wraplength=800, justify=LEFT)

        self.camera_label = Label(self.root)
        self.camera_label.grid(row=0, column=0)

        self.photo_btn = tk.Button(self.root, text="Snapshot!", command=self.take_snapshot)
        self.photo_btn.grid(row=0, column=0)
        self.root.bind('<space>', lambda event: self.take_snapshot())

        # Label for user feedback
        self.feedback_label = tk.Label(self.root, text="")
        self.feedback_label.grid(row=1, column=0)

        self.barcode_label = Label(self.root, text="Product Barcode:", anchor="w", justify='left')
        self.barcode_entry = Entry(self.root)
        self.barcode_entry.focus_set()
        self.get_untappd_button = Button(self.root, text="Haal Untappd gegevens", command=self.get_untappd, anchor="w", justify='left')

        self.price_label = Label(self.root, text="Product Price:", anchor="w", justify='left')
        self.price_entry = Entry(self.root)

        self.submit_button = Button(self.root, text="Maak product aan", command=self.submit_product, anchor="center", justify='center', bg='green')

        self.info_label.grid(row=1, column=0, columnspan=8, padx=10, pady=10, sticky="w")
        self.barcode_label.grid(row=2, column=0, padx=0, pady=5, sticky="w")
        self.barcode_entry.grid(row=2, column=1, padx=0, pady=5, sticky="w")
        self.get_untappd_button.grid(row=2, column=2, columnspan=1, sticky="w")

        self.price_label.grid(row=3, column=0, padx=0, pady=5, sticky="w")
        self.price_entry.grid(row=3, column=1, padx=0, pady=5, sticky="w")
        self.submit_button.grid(row=4, column=0, padx=10, pady=5, sticky="we", columnspan=3)

        self.vs = cv2.VideoCapture(0)
        self.video_loop()

    def video_loop(self):
        """ Get frame from the video stream and show it in Tkinter """
        ok, frame = self.vs.read()  # read frame from video stream
        if ok:  # frame captured without any errors
            cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)  # convert colors from BGR to RGBA
            self.current_image = Image.fromarray(cv2image)  # convert image for PIL
            imgtk = ImageTk.PhotoImage(image=self.current_image)  # convert image for tkinter
            self.camera_label.imgtk = imgtk  # anchor imgtk so it does not be deleted by garbage-collector
            self.camera_label.config(image=imgtk)  # show the image
        self.root.after(30, self.video_loop)

    def take_snapshot(self):
        """ Take snapshot and save it to the file """
        ts = datetime.datetime.now() # grab the current timestamp
        filename = "{}.jpg".format(ts.strftime("%Y-%m-%d_%H-%M-%S"))  # construct filename
        p = os.path.join("C:/Downloads", filename)  # construct output path
        self.current_image.save(p, "PNG")  # save image as jpeg file
        print("[INFO] saved {}".format(filename))
        self.feedback_label.config(text="Snapshot taken!")

    def run(self):
        print('run user interafce')
        self.root.mainloop()

    def get_untappd(self):
        print('Get untappd info')
        self.price_entry.insert(0, '9.5')

    def submit_product(self):
        # Add logic to handle submitted product information
        barcode = self.barcode_entry.get()
        price = self.price_entry.get()
        print('submit')
        print(barcode, price)


