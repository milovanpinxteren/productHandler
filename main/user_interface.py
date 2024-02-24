import tkinter
import tkinter as tk
from tkinter import Label, Entry, Button
import cv2
from PIL import Image, ImageTk
import datetime
import os
from tkcalendar import DateEntry

from Apis.product_creator import ProductCreator
from Apis.product_deletor import ProductDeletor
from Apis.quantity_updater import QuantityUpdater
from Apis.upload_image_to_shopify import ImageUploader
from data.lists import Lists
from Apis.existment_checker import ExistmentChecker
from label_printer.print_label_selection import SelectionLabelPrinter
from untappd_getter import UntappdGetter


class UserInterface:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("HoB Productinvoer en Labelprint")
        width = self.root.winfo_screenwidth()
        height = self.root.winfo_screenheight()
        self.root.geometry("%dx%d" % (width, height))
        self.root.columnconfigure(1, minsize=100, weight=0)

        # Create a frame with a grid layout
        self.grid_frame = tk.Frame(self.root)
        self.grid_frame.grid(row=0, column=0, sticky="nsew")

        self.column_width = int(width / 60)
        self.column_height = int(height / 300)
        self.productID = None
        self.image_counter = 0

        for i in range(8):
            self.grid_frame.columnconfigure(i, weight=1, uniform="foo")
        for i in range(20):
            self.grid_frame.rowconfigure(i, weight=1, uniform="foo")

        for i in range(20):
            for j in range(8):
                label = tk.Label(self.grid_frame, anchor="w", height=self.column_height, width=self.column_width,
                                 text="", borderwidth=1, relief="groove")
                label.grid(row=i, column=j, sticky="nsew")

        self.initialize_widgets()
        self.image_uploader = ImageUploader()
        self.product_creator = ProductCreator()
        self.quantity_updater = QuantityUpdater()
        self.product_deletor = ProductDeletor()
        self.existment_checker = ExistmentChecker()
        self.selection_label_printer = SelectionLabelPrinter()

    def run(self):
        self.root.mainloop()

    def video_loop(self):
        """ Get frame from the video stream and show it in Tkinter """
        ok, frame = self.vs.read()  # read frame from video stream
        if ok:  # frame captured without any errors
            cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
            cropped_image = cv2image[:, 100:(cv2image.shape[1] - 100), :]

            self.current_image = Image.fromarray(cropped_image) # convert image for PIL
            imgtk = ImageTk.PhotoImage(image=self.current_image)  # convert image for tkinter
            self.camera_label.imgtk = imgtk  # anchor imgtk so it does not be deleted by garbage-collector
            self.camera_label.config(image=imgtk)  # show the image
        self.root.after(30, self.video_loop)

    def take_snapshot(self):
        """ Take snapshot and save it to the file """
        ts = datetime.datetime.now()  # grab the current timestamp
        filename = "{}.jpg".format(ts.strftime("%Y-%m-%d_%H-%M-%S"))  # construct filename
        # p = os.path.join("C:/Downloads", filename)  # construct output path
        # self.current_image.save(p, "PNG")  # save image as jpeg file
        # print("[INFO] saved {}".format(filename))

        timestamp = ts.strftime("%Y-%m-%d_%H-%M-%S")

        image_uploaded, status_code = self.image_uploader.upload_image_to_shopify(self.productID, self.current_image)
        if image_uploaded:
            self.image_counter += 1
            self.feedback_label.config(text=f"Foto {self.image_counter} geüpload naar Shopify om {timestamp}")
        else:
            self.feedback_label.config(text=f"Foto niet geüpload Probeer opnieuw of roep Milo. Foutmelding: {status_code}")

    def initialize_widgets(self):
        self.item_brand_label = Label(self.grid_frame, text="Merk (bij titel):")
        self.item_brand_label.grid(row=0, column=0, sticky=tk.W)
        self.brand_value_inside = tkinter.StringVar(self.grid_frame)
        self.brand_value_inside.set("Overig")
        self.item_brand_entry = tk.OptionMenu(self.grid_frame, self.brand_value_inside, *Lists.brand_options)
        self.item_brand_entry.grid(row=0, column=0, sticky=tk.E)

        self.brand_search_entry = tk.Entry(self.grid_frame)
        self.brand_search_entry.grid(row=0, column=1, sticky=tk.W)
        self.brand_search_entry.bind("<KeyRelease>", self.filter_brands)

        self.item_country_label = Label(self.grid_frame, text="Land:")
        self.country_value_inside = tkinter.StringVar(self.grid_frame)
        self.country_value_inside.set("Overig")
        self.item_country_label.grid(row=0, column=2, sticky=tk.W)
        self.item_country_entry = tk.OptionMenu(self.grid_frame, self.country_value_inside, *Lists.country_options)
        self.item_country_entry.grid(row=0, column=2, sticky=tk.E)

        self.country_search_entry = tk.Entry(self.grid_frame)
        self.country_search_entry.grid(row=0, column=3, sticky=tk.W)
        self.country_search_entry.bind("<KeyRelease>", self.filter_countries)

        self.item_type_label = Label(self.grid_frame, text="Soort bier:")
        self.type_value_inside = tkinter.StringVar(self.grid_frame)
        self.type_value_inside.set("Overig")
        self.item_type_label.grid(row=0, column=4, sticky=tk.W)
        self.item_type_entry = tk.OptionMenu(self.grid_frame, self.type_value_inside, *Lists.beer_type_options)
        self.item_type_entry.grid(row=0, column=4, sticky=tk.E)

        self.type_search_entry = tk.Entry(self.grid_frame)
        self.type_search_entry.grid(row=0, column=5, sticky=tk.W)
        self.type_search_entry.bind("<KeyRelease>", self.filter_types)

        self.aging_method_label = Label(self.grid_frame, text="Rijpingsmethode:")
        self.aging_value_inside = tkinter.StringVar(self.grid_frame)
        self.aging_value_inside.set("Niet Barrel Aged")
        self.aging_method_label.grid(row=0, column=6, sticky=tk.W)
        self.aging_method_entry = tk.OptionMenu(self.grid_frame, self.aging_value_inside, *Lists.aging_methods)
        self.aging_method_entry.grid(row=0, column=7, sticky=tk.W)

        #############################################ROW 2##############################################################

        self.barcode_label = Label(self.grid_frame, text="Product Barcode:")
        self.barcode_label.grid(row=1, column=0, sticky=tk.W)
        self.barcode_entry = Entry(self.grid_frame, width=15)
        self.barcode_entry.grid(row=1, column=1, sticky=tk.W)

        self.title_label = Label(self.grid_frame, text="Product Titel:")
        self.title_label.grid(row=1, column=2, sticky=tk.W)
        self.title_entry = Entry(self.grid_frame, width=self.column_width * 4)
        self.title_entry.grid(row=1, column=3, sticky=tk.W, columnspan=3)

        self.price_label = Label(self.grid_frame, text="Product Prijs (b.v.: 12.95):")
        self.price_label.grid(row=1, column=6, sticky=tk.W)
        self.price_entry = Entry(self.grid_frame)
        self.price_entry.grid(row=1, column=7, sticky=tk.W)

        #############################################ROW 3##############################################################

        self.description_label = Label(self.grid_frame, text="Product Beschrijving:")
        self.description_label.grid(row=2, column=0, sticky=tk.W)
        self.description_entry = Entry(self.grid_frame, width=self.column_width * 8)
        self.description_entry.grid(row=2, column=1, columnspan=7, sticky=tk.W)

        #############################################ROW 4##############################################################

        self.available_amount_label = Label(self.grid_frame, text="Aantal beschikbaar:")
        self.available_amount_label.grid(row=3, column=0, sticky=tk.W)
        self.available_amount_entry = Entry(self.grid_frame, width=4)
        self.available_amount_entry.grid(row=3, column=0, sticky=tk.E)

        self.item_weight_label = Label(self.grid_frame, text="Gewicht (in gram):")
        self.item_weight_label.grid(row=3, column=1, sticky=tk.W)
        self.item_weight_entry = Entry(self.grid_frame, width=5)
        self.item_weight_entry.grid(row=3, column=1, sticky=tk.E)

        self.item_brewyear_label = Label(self.grid_frame, text="Brouwjaar (bij titel):")
        self.item_brewyear_label.grid(row=3, column=2, sticky=tk.W)
        self.item_brewyear_entry = Entry(self.grid_frame)
        self.item_brewyear_entry.grid(row=3, column=3, sticky=tk.W)

        self.item_percentage_label = Label(self.grid_frame, text="Alcoholpercentage:")
        self.item_percentage_label.grid(row=3, column=4, sticky=tk.W)
        self.item_percentage_entry = Entry(self.grid_frame)
        self.item_percentage_entry.grid(row=3, column=4, sticky=tk.E)

        self.item_statiegeld_label = Label(self.grid_frame, text="Statiegeld:")
        self.statiegeld_value_inside = tkinter.StringVar(self.grid_frame)
        self.statiegeld_value_inside.set(str(0.0))
        self.item_statiegeld_label.grid(row=3, column=5, sticky=tk.W)
        self.item_statiegeld_entry = tk.OptionMenu(self.grid_frame, self.statiegeld_value_inside, *Lists.statiegeld_options)
        self.item_statiegeld_entry.grid(row=3, column=5, sticky=tk.E)

        self.item_volume_label = Label(self.grid_frame, text="Volume (in CL) (bij titel):")
        self.volume_value_inside = tkinter.StringVar(self.grid_frame)
        self.volume_value_inside.set("33 CL")
        self.item_volume_label.grid(row=3, column=6, sticky=tk.W)
        self.item_volume_entry = tk.OptionMenu(self.grid_frame, self.volume_value_inside, *Lists.volume_options)
        self.item_volume_entry.grid(row=3, column=7, sticky=tk.W)

        self.submit_button = Button(self.grid_frame, text="Maak product aan", command=self.submit_product, anchor="center",
                                    justify='center', bg='green')
        self.submit_button.grid(row=4, column=0, padx=10, pady=5, sticky="we", columnspan=8)

        self.camera_label = Label(self.grid_frame)
        self.camera_label.grid(row=5, column=0, columnspan=4, rowspan=12)
        self.photo_btn = tk.Button(self.grid_frame, text="Verzend naar Shopify", command=self.take_snapshot, state="disabled")
        self.photo_btn.grid(row=8, column=4)

        self.feedback_label = tk.Label(self.grid_frame,
                                       text="Druk op knop om foto naar shopify te uploaden. (Eerst moet product gemaakt zijn)")
        self.feedback_label.grid(row=9, column=4, columnspan=5)

        self.vs = cv2.VideoCapture(0)
        self.video_loop()

        self.check_barcode_existment_label = Label(self.grid_frame, text="Barcode/titel voor check in systeem:")
        self.check_barcode_existment_label.grid(row=17, column=0, sticky=tk.W)
        self.check_barcode_existment_entry = Entry(self.grid_frame, width=15)
        self.check_barcode_existment_entry.grid(row=17, column=1, sticky=tk.W)
        self.check_barcode_existment_button = Button(self.grid_frame, text="Check in systeem", command=self.check_barcode_existment, anchor="center",
                                    justify='center', bg='yellow')
        self.check_barcode_existment_button.grid(row=17, column=2)

        self.print_label_button = Button(self.grid_frame, text="Print Label", command=self.print_label, anchor="center",
                                    justify='center', bg='green', state="disabled")
        self.print_label_button.grid(row=17, column=3)

        self.check_barcode_existment_feedback_label = Label(self.grid_frame, text="Vul eerst barcode/titel in, en druk op 'check in systeem'")
        self.check_barcode_existment_feedback_label.grid(row=17, column=4, columnspan=5, sticky=tk.W)

        self.min_date_label = Label(self.grid_frame, text="print labels vanaf:")
        self.min_date_label.grid(row=13, column=4, columnspan=1, sticky=tk.W)
        self.min_date_picker = DateEntry(self.grid_frame)
        self.min_date_picker.grid(row=13, column=4, sticky=tk.E)

        self.min_time_label = Label(self.grid_frame, text="Tijd vanaf (b.v. 12:30):")
        self.min_time_label.grid(row=13, column=5, columnspan=1, sticky=tk.W)
        self.default_min_time = tk.StringVar(value="00:00")
        self.min_time_picker = Entry(self.grid_frame, textvariable=self.default_min_time)
        self.min_time_picker.grid(row=13, column=6, sticky=tk.W)

        self.max_date_label = Label(self.grid_frame, text="print labels tot:")
        self.max_date_label.grid(row=14, column=4, columnspan=1, sticky=tk.W)
        self.max_date_picker = DateEntry(self.grid_frame)
        self.max_date_picker.grid(row=14, column=4, sticky=tk.E)

        self.max_time_label = Label(self.grid_frame, text="Tijd tot (b.v. 12:30):")
        self.max_time_label.grid(row=14, column=5, columnspan=1, sticky=tk.W)
        self.default_max_time = tk.StringVar(value="00:00")
        self.max_time_picker = Entry(self.grid_frame, textvariable=self.default_max_time)
        self.max_time_picker.grid(row=14, column=6, sticky=tk.W)

        self.get_untappd_button = tk.Button(self.grid_frame, text="Haal Untappd Gegevens op", command=self.get_untappd, bg='lightgreen')
        self.get_untappd_button.grid(row=15, column=4, padx=10, pady=5, sticky="we", columnspan=1)

        self.print_label_selection = tk.Button(self.grid_frame, text="Print selectie labels", command=self.print_label_selection, bg='lightgreen')
        self.print_label_selection.grid(row=15, column=5, padx=10, pady=5, sticky="we", columnspan=1)

        self.next_product_button = tk.Button(self.grid_frame, text="Volgend Product", command=self.next_product, bg='orange')
        self.next_product_button.grid(row=18, column=0, padx=10, pady=5, sticky="we", columnspan=8)

    def submit_product(self):
        barcode = self.barcode_entry.get()
        title = self.title_entry.get()
        price = self.price_entry.get().replace(',', '.')

        description = self.description_entry.get()

        available_amount = self.available_amount_entry.get()
        item_weight = self.item_weight_entry.get().replace(',', '.')
        item_volume = self.volume_value_inside.get()
        percentage = self.item_percentage_entry.get().replace(',', '.')
        body_html = self.generate_html(description, item_volume, percentage)
        brew_year = self.item_brewyear_entry.get()
        statiegeld = 'Statiegeld: ' + self.statiegeld_value_inside.get()

        brand = self.brand_value_inside.get()
        country = self.country_value_inside.get()
        beer_type = self.type_value_inside.get()
        aging_method = self.aging_value_inside.get()

        if brew_year != '' and item_volume != '' and brand in Lists.brand_options and brand != "Overig":
            shopify_title = brand + " " + title + " " + brew_year + " - " + item_volume
        elif brew_year != '' and item_volume != '' and brand == "Overig":
            shopify_title = title + " " + brew_year + " - " + item_volume

        elif brew_year != '' and item_volume == '' and brand == "Overig":
            shopify_title = title + " " + brew_year
        elif brew_year != '' and item_volume == '' and brand in Lists.brand_options and brand != "Overig":
            shopify_title = brand + " " + title + " " + brew_year

        elif brew_year == '' and item_volume != '' and brand == "Overig":
            shopify_title = title + " - " + item_volume
        elif brew_year == '' and item_volume != '' and brand in Lists.brand_options and brand != "Overig":
            shopify_title = brand + " " + title + " - " + item_volume

        elif brew_year == '' and item_volume == '' and brand == "Overig":
            shopify_title = title
        elif brew_year == '' and item_volume == '' and brand in Lists.brand_options and brand != "Overig":
            shopify_title = brand + " " + title

        data_to_create = {'title': shopify_title,
                          "body_html": body_html,
                          "tags": statiegeld,
                          "variants": [{
                              "barcode": barcode,
                              "price": price,
                              "grams": item_weight,
                              "inventory_management": "shopify",
                          }],
                          "metafields": [
                              {"key": "brouwjaar", "value": brew_year, "type": "number_integer", "namespace": "custom"},
                              {"key": "merk", "value": brand, "type": "single_line_text_field", "namespace": "custom"},
                              {"key": "land_van_herkomst", "value": country, "type": "single_line_text_field", "namespace": "custom"},
                              {"key": "inhoud", "value": item_volume, "type": "single_line_text_field", "namespace": "custom"},
                              {"key": "soort_bier", "value": beer_type, "type": "single_line_text_field", "namespace": "custom"},
                              {"key": "rijpingsmethode", "value": aging_method, "type": "single_line_text_field", "namespace": "custom"},
                              {"key": "alcoholpercentage", "value": percentage, "type": "number_decimal", "namespace": "custom"}
                              ]}

        try:
            self.productID, self.variantID, self.inventory_item_id = self.product_creator.create_product_on_shopify(
                data_to_create)
            if self.productID:
                quantity_updated = self.quantity_updater.update_quantity(self.inventory_item_id, available_amount)
                if quantity_updated:
                    self.photo_btn['state'] = "normal"
                    self.feedback_label.config(
                        text="Product toegevoegd, voeg nu foto's toe. Ga daarna naar het volgende product")
                else:
                    self.feedback_label.config(
                        text="Beschikbare hoeveelheid niet doorgevoerd. Controleer of alle velden goed zijn ingevuld")
                    self.product_deletor.delete_product(self.productID)
            else:
                self.feedback_label.config(
                    text="Product aanmaken niet gelukt. Controleer of alle velden goed zijn ingevuld")
        except TypeError:
            self.feedback_label.config(
                text="Product aanmaken niet gelukt. Controleer of alle velden goed zijn ingevuld")

    def generate_html(self, description, item_volume, percentage):
        body_html = f"""
        <p>{description}</p><br>
        <h3>Productdetails:</h3>
        <ul>
        <li><b>Alcoholpercentage: </b><i>{percentage}%</i></li>
        <li><b>Volume: </b><i>{item_volume}</i></li>
        </ul>
        """
        return body_html

    def filter_brands(self, event):
        search_query = self.brand_search_entry.get().lower()
        list_to_filter = Lists.brand_options
        filtered_brands = [item for item in list_to_filter if search_query in item.lower()]
        menu = self.item_brand_entry["menu"]
        menu.delete(0, "end")
        for brand in filtered_brands:
            self.brand_value_inside.set(brand)

    def filter_countries(self, event):
        search_query = self.country_search_entry.get().lower()
        list_to_filter = Lists.country_options
        filtered_countries = [item for item in list_to_filter if search_query in item.lower()]
        menu = self.item_country_entry["menu"]
        menu.delete(0, "end")
        for country in filtered_countries:
            self.country_value_inside.set(country)

    def filter_types(self, event):
        search_query = self.type_search_entry.get().lower()
        list_to_filter = Lists.beer_type_options
        filtered_types = [item for item in list_to_filter if search_query in item.lower()]
        menu = self.item_type_entry["menu"]
        menu.delete(0, "end")
        for type in filtered_types:
            self.type_value_inside.set(type)

    def check_barcode_existment(self):
        barcode_value = self.check_barcode_existment_entry.get()
        found_product = self.existment_checker.check_existment(barcode_value)
        print(found_product)
        self.check_barcode_existment_feedback_label.config(text=found_product[1])
        if found_product:
            self.print_label_button['state'] = 'normal'

    def print_label(self):
        product_url = self.check_barcode_existment_feedback_label.cget("text")
        self.existment_checker.print_label(product_url)

    def print_label_selection(self):
        min_date = self.min_date_picker.get_date()
        min_time = self.min_time_picker.get()
        max_date = self.max_date_picker.get_date()
        max_time = self.max_time_picker.get()
        min_time_for_query = str(min_time) + ':00-00:00'
        max_time_for_query = str(max_time) + ':00-00:00'
        query = f'created_at_min={min_date} {min_time_for_query}&created_at_max={max_date} {max_time_for_query}'
        self.selection_label_printer.print_labels(query)

    def get_untappd(self):
        untappd_getter = UntappdGetter()
        untappd_updated = untappd_getter.get_untappd()
        if untappd_updated == 'done':
            self.feedback_label.config(text="Untappd gegevens geüpdated, klaar om labels te printen")



    def next_product(self):
        # Clear all values and set focus on barcode_entry
        self.brand_value_inside.set("Overig")
        self.country_value_inside.set("Overig")
        self.type_value_inside.set("Overig")
        self.aging_value_inside.set("Niet Barrel Aged")
        self.barcode_entry.delete(0, 'end')
        self.title_entry.delete(0, 'end')
        self.description_entry.delete(0, 'end')
        self.price_entry.delete(0, 'end')
        self.available_amount_entry.delete(0, 'end')
        self.item_weight_entry.delete(0, 'end')
        self.item_brewyear_entry.delete(0, 'end')
        self.item_percentage_entry.delete(0, 'end')
        self.volume_value_inside.set("33 CL")
        self.photo_btn['state'] = "disabled"
        self.productID = None
        self.feedback_label.config(
            text="Maak eerst het product aan, voeg daarna de fotos aan het product toe.")
        self.barcode_entry.focus_set()
