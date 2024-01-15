import tkinter as tk
from tkinter import Label, Entry, Button, WORD, LEFT
import cv2


class UserInterface:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Product Information Entry")
        self.info_label = Label(self.root, text="Flow: 1. Scan barcode, en haal Untappd gegevens op. 2. Vul de titel in (na de suggestie van Untappd) 3. Maak foto's en verstuur deze naar Shopify. 4. Controleer of de url van de foto's zijn toegevoegd. 5. Vul de missende gegevens in en druk op Verzenden naar Shopify", wraplength=800, justify=LEFT)

        self.barcode_label = Label(self.root, text="Product Barcode:", anchor="w", justify='left')
        self.barcode_entry = Entry(self.root)
        self.barcode_entry.focus_set()
        # self.barcode_entry.bind("<KeyRelease-Return>", self.get_untappd)
        self.get_untappd_button = Button(self.root, text="Haal Untappd gegevens", command=self.get_untappd, anchor="w", justify='left')

        # TODO: listen for barcode (if filled in and min chars)
        # TODO: send request to Untappd
        # TODO: automaticly fill in info from untappd

        self.price_label = Label(self.root, text="Product Price:", anchor="w", justify='left')
        self.price_entry = Entry(self.root)

        self.submit_button = Button(self.root, text="Maak product aan", command=self.submit_product, anchor="w", justify='left')
        self.initialize_webcam()

        self.info_label.grid(row=0, column=0, columnspan=8, padx=10, pady=10, sticky="w")
        self.barcode_label.grid(row=1, column=0, padx=0, pady=5, sticky="w")
        self.barcode_entry.grid(row=1, column=1, padx=0, pady=5, sticky="w")
        self.get_untappd_button.grid(row=1, column=2, columnspan=1, sticky="w")

        self.price_label.grid(row=2, column=0, padx=0, pady=5, sticky="w")
        self.price_entry.grid(row=2, column=1, padx=0, pady=5, sticky="w")

        # self.scan_button.grid(row=2, column=0, columnspan=2, pady=10)
        # self.scan_result_label.grid(row=3, column=0, columnspan=2, pady=10)

    def initialize_webcam(self):
        self.cap = cv2.VideoCapture(0)
        self.cap.set(3, 640)  # Set width
        self.cap.set(4, 480)  # Set height

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
