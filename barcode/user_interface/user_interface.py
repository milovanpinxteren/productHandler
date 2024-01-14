import tkinter as tk
from tkinter import Label, Entry, Button
import cv2

class UserInterface:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Product Information Entry")

        self.barcode_label = Label(self.root, text="Product Barcode:")
        self.barcode_entry = Entry(self.root)
        self.barcode_entry.focus_set()

        self.price_label = Label(self.root, text="Product Price:")
        self.price_entry = Entry(self.root)

        # self.scan_button = Button(self.root, text="Scan Barcode", command=self.scan_barcode)
        # self.scan_result_label = Label(self.root, text="Scanned Barcode: ")

        self.initialize_webcam()

        self.barcode_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.barcode_entry.grid(row=0, column=1, padx=10, pady=10)

        self.price_label.grid(row=1, column=0, padx=10, pady=10, sticky="w")
        self.price_entry.grid(row=1, column=1, padx=10, pady=10)

        # self.scan_button.grid(row=2, column=0, columnspan=2, pady=10)
        # self.scan_result_label.grid(row=3, column=0, columnspan=2, pady=10)

    def initialize_webcam(self):
        self.cap = cv2.VideoCapture(0)
        self.cap.set(3, 640)  # Set width
        self.cap.set(4, 480)  # Set height


    def run(self):
        print('run user interafce')
        self.root.mainloop()