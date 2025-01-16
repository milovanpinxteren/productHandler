import tkinter
import tkinter as tk
from tkinter import Label, Entry, Button
import cv2
import requests
from PIL import Image, ImageTk, ImageEnhance
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
from microcash_importer.microcash_import_maker import MicrocashProductMaker
import re
import random
from dotenv import load_dotenv
import os
import json

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

        # for i in range(6):
        #     self.grid_frame.columnconfigure(i, weight=1, uniform="foo")
        # for i in range(4):
        #     self.grid_frame.rowconfigure(i, weight=1, uniform="foo")

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
        self.microcash_import_maker = MicrocashProductMaker()
        self.untappd_getter = UntappdGetter()

    def run(self):
        self.root.mainloop()

    def video_loop(self):
        """ Capture frame from the video stream, process it, and display a scaled-down version in Tkinter """
        ok, frame = self.vs.read()  # Capture a frame from the webcam
        if ok:
            # Store the full-resolution frame in self.current_image
            full_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)  # Convert to RGBA
            self.current_image = Image.fromarray(full_frame)  # Save full frame for snapshots

            # Get display size for resizing, with smaller scaling factors
            display_width = max(int(self.root.winfo_width() * 0.5), 480)  # Scale width to 50% of window or min 480
            display_height = max(int(self.root.winfo_height() * 0.5), 360)  # Scale height to 50% of window or min 360

            # Calculate aspect ratio of the full frame
            original_height, original_width, _ = full_frame.shape
            aspect_ratio = original_width / original_height

            # Adjust display dimensions to maintain aspect ratio
            if display_width / display_height > aspect_ratio:
                display_width = int(display_height * aspect_ratio)
            else:
                display_height = int(display_width / aspect_ratio)

            # Resize frame for display
            resized_frame = cv2.resize(full_frame, (display_width, display_height), interpolation=cv2.INTER_AREA)

            # Convert resized frame to PIL Image for display in Tkinter
            display_image = Image.fromarray(resized_frame)

            # Update Tkinter label
            imgtk = ImageTk.PhotoImage(image=display_image)
            self.camera_label.imgtk = imgtk  # Anchor to prevent garbage collection
            self.camera_label.config(image=imgtk)  # Display resized image

        # Schedule the next frame
        self.root.after(30, self.video_loop)

    def take_snapshot(self):
        """ Take snapshot and save it to the file """
        ts = datetime.datetime.now()  # grab the current timestamp
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
        self.available_amount_entry.grid(row=3, column=0, sticky=tk.E, padx=55, pady=5)

        self.item_weight_label = Label(self.grid_frame, text="Gewicht (in gram):")
        self.item_weight_label.grid(row=3, column=1, sticky=tk.W)
        self.item_weight_entry = Entry(self.grid_frame, width=7)
        self.item_weight_entry.grid(row=3, column=1, sticky=tk.E, padx=45, pady=5)

        self.item_brewyear_label = Label(self.grid_frame, text="Brouwjaar (bij titel):")
        self.item_brewyear_label.grid(row=3, column=2, sticky=tk.W)
        self.item_brewyear_entry = Entry(self.grid_frame, width=5)
        self.item_brewyear_entry.grid(row=3, column=2, sticky=tk.E, padx=50, pady=5)

        self.item_percentage_label = Label(self.grid_frame, text="Alcoholpercentage:")
        self.item_percentage_label.grid(row=3, column=3, sticky=tk.W)
        self.item_percentage_entry = Entry(self.grid_frame, width=3)
        self.item_percentage_entry.grid(row=3, column=3, sticky=tk.E, padx=70, pady=5)

        self.item_statiegeld_label = Label(self.grid_frame, text="Statiegeld:")
        self.statiegeld_value_inside = tkinter.StringVar(self.grid_frame)
        self.statiegeld_value_inside.set(str(0.0))
        self.item_statiegeld_label.grid(row=3, column=4, sticky=tk.W)
        self.item_statiegeld_entry = tk.OptionMenu(self.grid_frame, self.statiegeld_value_inside, *Lists.statiegeld_options)
        self.item_statiegeld_entry.grid(row=3, column=4, sticky=tk.E, padx=55, pady=5)

        self.item_volume_label = Label(self.grid_frame, text="Volume (in CL) (bij titel):")
        self.volume_value_inside = tkinter.StringVar(self.grid_frame)
        self.volume_value_inside.set("33 CL")
        self.item_volume_label.grid(row=3, column=5, sticky=tk.W)
        self.item_volume_entry = tk.OptionMenu(self.grid_frame, self.volume_value_inside, *Lists.volume_options)
        self.item_volume_entry.grid(row=3, column=5, sticky=tk.E)

        self.item_tax_label = Label(self.grid_frame, text="BTW:")
        self.item_tax_inside = tkinter.StringVar(self.grid_frame)
        self.item_tax_inside.set("H")
        self.item_tax_label.grid(row=3, column=6, sticky=tk.W)
        self.item_tax_entry = tk.OptionMenu(self.grid_frame, self.item_tax_inside, *Lists.tax_options)
        self.item_tax_entry.grid(row=3, column=6, sticky=tk.E, padx=65, pady=5)

        self.submit_button = Button(self.grid_frame, text="Maak product aan", command=self.submit_product, anchor="center",
                                    justify='center', bg='green')
        self.submit_button.grid(row=4, column=0, padx=10, pady=5, sticky="we", columnspan=8)


        self.vs = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        self.vs.set(cv2.CAP_PROP_FRAME_WIDTH, 3840)
        self.vs.set(cv2.CAP_PROP_FRAME_HEIGHT, 2160)
        self.vs.set(cv2.CAP_PROP_AUTOFOCUS, 1)
        width = self.vs.get(cv2.CAP_PROP_FRAME_WIDTH)
        height = self.vs.get(cv2.CAP_PROP_FRAME_HEIGHT)
        autofocus = self.vs.get(cv2.CAP_PROP_AUTOFOCUS)

        print(f"Resolution: {width}x{height}")
        print(f"Autofocus enabled: {bool(autofocus)}")
        # if self.vs.get(cv2.CAP_PROP_AUTOFOCUS) != 1:
        #     self.vs.set(cv2.CAP_PROP_AUTOFOCUS, 1)
        self.camera_label = Label(self.grid_frame)
        self.camera_label.grid(row=5, column=0, columnspan=4, rowspan=12, sticky="nsew")
        self.video_loop()

        self.photo_btn = tk.Button(self.grid_frame, text="Verzend naar Shopify", command=self.take_snapshot, state="disabled")
        self.photo_btn.grid(row=8, column=4)


        self.feedback_label = tk.Label(self.grid_frame,
                                       text="Druk op knop om foto naar shopify te uploaden. (Eerst moet product gemaakt zijn)")
        self.feedback_label.grid(row=9, column=4, columnspan=5)



        self.check_barcode_existment_label = Label(self.grid_frame, text="Barcode/titel voor check in systeem:")
        self.check_barcode_existment_label.grid(row=17, column=0, sticky=tk.W)
        self.check_barcode_existment_entry = Entry(self.grid_frame, width=15)
        self.check_barcode_existment_entry.grid(row=17, column=1, sticky=tk.W)
        self.check_barcode_existment_button = Button(self.grid_frame, text="Check in systeem", command=self.check_barcode_existment, anchor="center",
                                    justify='center', bg='yellow')
        self.check_barcode_existment_button.grid(row=17, column=2)

        self.update_untappd_button = Button(self.grid_frame, text="Update Untappd van product", command=self.update_untappd, anchor="center",
                                    justify='center', bg='yellow', state="disabled")
        self.update_untappd_button.grid(row=17, column=3)

        self.print_label_button = Button(self.grid_frame, text="Print Label", command=self.print_label, anchor="center",
                                    justify='center', bg='green', state="disabled")
        self.print_label_button.grid(row=17, column=4)

        self.check_barcode_existment_feedback_label = Label(self.grid_frame, text="Vul eerst barcode/titel in, en druk op 'check in systeem'")
        self.check_barcode_existment_feedback_label.grid(row=17, column=5, columnspan=5, sticky=tk.W)

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
        self.default_max_time = tk.StringVar(value="23:59")
        self.max_time_picker = Entry(self.grid_frame, textvariable=self.default_max_time)
        self.max_time_picker.grid(row=14, column=6, sticky=tk.W)

        self.get_untappd_button = tk.Button(self.grid_frame, text="Haal Untappd Gegevens op", command=self.get_untappd, bg='lightgreen')
        self.get_untappd_button.grid(row=15, column=4, padx=10, pady=5, sticky="we", columnspan=1)

        self.print_label_selection = tk.Button(self.grid_frame, text="Print selectie labels", command=self.print_label_selection, bg='lightgreen')
        self.print_label_selection.grid(row=15, column=5, padx=10, pady=5, sticky="we", columnspan=1)

        self.prepare_microcash_import_button = tk.Button(self.grid_frame, text="Zet import klaar", command=self.prepare_microcash_import, bg='lightblue')
        self.prepare_microcash_import_button.grid(row=15, column=6, padx=10, pady=5, sticky="we", columnspan=1)

        self.next_product_button = tk.Button(self.grid_frame, text="Volgend Product", command=self.next_product, bg='orange')
        self.next_product_button.grid(row=18, column=0, padx=10, pady=5, sticky="we", columnspan=8)

    def get_ai_answer(self, text):
        load_dotenv()
        eden_ai_token = os.environ["EDEN_AI_TOKEN"]
        edenAI_headers = {
            "Authorization": eden_ai_token}
        url = "https://api.edenai.run/v2/text/generation"
        providers_list = ['openai']  # mistral
        # providers_list = ['cohere/command-light']  # mistral

        random_provider = random.choice(providers_list)
        payload = {
            "providers": random_provider,
            "text": text,
            "temperature": 0.6,
            "max_tokens": 500,
        }

        # if random_provider == "cohere":
        #     payload["model"] = "command"  # Adjust based on available models
        response = requests.post(url, json=payload, headers=edenAI_headers)
        result = json.loads(response.text)
        print(result)
        provider = next(iter(result))
        return result, provider

    def submit_product(self):
        self.image_counter = 0
        barcode = self.barcode_entry.get()
        title = self.title_entry.get()
        price = self.price_entry.get().replace(',', '.')

        description = self.description_entry.get()

        available_amount = self.available_amount_entry.get()
        item_weight = self.item_weight_entry.get().replace(',', '.')
        try:
            item_weight = float(item_weight)
        except ValueError:
            item_weight = 300
        item_volume = self.volume_value_inside.get()
        percentage = self.item_percentage_entry.get().replace(',', '.')
        body_html = self.generate_html(description, item_volume, percentage)
        brew_year = self.item_brewyear_entry.get()
        statiegeld = 'Statiegeld: ' + self.statiegeld_value_inside.get()

        brand = self.brand_value_inside.get()
        country = self.country_value_inside.get()
        beer_type = self.type_value_inside.get()
        aging_method = self.aging_value_inside.get()
        tax_value = self.item_tax_inside.get()
        if tax_value == 'H':
            taxable = True
            btw_tag = 'BTW Hoog'
        elif tax_value == 'L':
            taxable = True
            btw_tag = 'BTW Laag'
        elif tax_value == '0':
            taxable = False
            btw_tag = 'BTW 0'

        if beer_type != 'Overig':
            beer_type_str = ' ' + beer_type
        else:
            beer_type_str = ''


        if brew_year != '' and item_volume != '' and brand in Lists.brand_options and brand != "Overig":
            shopify_title = brand + " " + title + " " + brew_year + beer_type_str + " - " + item_volume
            seo_title = brand + " " + title + " " + brew_year + beer_type_str + " bier" + " - " + item_volume

        elif brew_year != '' and item_volume != '' and brand == "Overig":
            shopify_title = title + " " + brew_year + beer_type_str + " - " + item_volume
            seo_title = title + " " + brew_year + beer_type_str + " bier" + " - " + item_volume
        elif brew_year != '' and item_volume == '' and brand == "Overig":
            shopify_title = title + " " + brew_year + beer_type_str
            seo_title = title + " " + brew_year + beer_type_str + ' bier'
        elif brew_year != '' and item_volume == '' and brand in Lists.brand_options and brand != "Overig":
            shopify_title = brand + " " + title + " " + brew_year + beer_type_str
            seo_title = brand + " " + title + " " + brew_year + beer_type_str + ' bier'

        elif brew_year == '' and item_volume != '' and brand == "Overig":
            shopify_title = title + beer_type_str + " - " + item_volume
            seo_title = title + beer_type_str + " bier" + " - " + item_volume
        elif brew_year == '' and item_volume != '' and brand in Lists.brand_options and brand != "Overig":
            shopify_title = brand + " " + title + beer_type_str + " - " + item_volume
            seo_title = brand + " " + title + beer_type_str + ' bier' + " - " + item_volume
        elif brew_year == '' and item_volume == '' and brand == "Overig":
            shopify_title = title + beer_type_str
            seo_title = title + beer_type_str + ' bier'
        elif brew_year == '' and item_volume == '' and brand in Lists.brand_options and brand != "Overig":
            shopify_title = brand + " " + title + beer_type_str
            seo_title = brand + " " + title + beer_type_str + ' bier'

        seo_title = re.sub(r'\s{2,}', ' ', seo_title)
        shopify_title = re.sub(r'\s{2,}', ' ', shopify_title)
        new_handle = seo_title.replace(' ', '-')
        new_handle = re.sub(r'-{2,}', '-', new_handle)

        ai_response, provider = self.get_ai_answer(
            f"schrijf een korte SEO/Meta description van max 2 zinnen over {seo_title}")
        if 'detail' not in ai_response:
            prompt_answer = ai_response[provider]['standardized_response']['generated_text']
            seo_description = "\n".join([line.strip() for line in prompt_answer.splitlines() if line.strip()])
            cleaned_seo_description = seo_description.replace('"', '')
        else:
            self.feedback_label.config(
                text=f"AI model fout: {ai_response}")

        data_to_create = {'title': shopify_title,
                          'handle': new_handle,
                          "body_html": body_html,
                          "tags": statiegeld + ', ' + btw_tag,
                          "seo": {
                              "description": cleaned_seo_description,
                              "title": seo_title
                          },
                          "variants": [{
                              "barcode": barcode,
                              "price": price,
                              "grams": item_weight,
                              "inventory_management": "SHOPIFY",
                              "taxable": taxable,
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

        # Clear existing menu items
        self.item_brand_entry['menu'].delete(0, 'end')

        # Add filtered options to the OptionMenu
        for brand in filtered_brands:
            self.item_brand_entry['menu'].add_command(label=brand,
                                                      command=tk._setit(self.brand_value_inside, brand))

        # Automatically set the first matching value, or reset if no match
        if filtered_brands:
            self.brand_value_inside.set(filtered_brands[0])
        else:
            self.brand_value_inside.set('Overig')

    def filter_countries(self, event):
        search_query = self.country_search_entry.get().lower()
        list_to_filter = Lists.country_options
        filtered_countries = [item for item in list_to_filter if search_query in item.lower()]

        # Clear existing menu items
        self.item_country_entry['menu'].delete(0, 'end')

        # Add filtered options to the OptionMenu
        for country in filtered_countries:
            self.item_country_entry['menu'].add_command(label=country,
                                                        command=tk._setit(self.country_value_inside, country))

        # Automatically set the first matching value, or reset if no match
        if filtered_countries:
            self.country_value_inside.set(filtered_countries[0])
        else:
            self.country_value_inside.set('Overig')

    def filter_types(self, event):
        search_query = self.type_search_entry.get().lower()
        list_to_filter = Lists.beer_type_options
        filtered_types = [item for item in list_to_filter if search_query in item.lower()]

        # Clear existing menu items
        self.item_type_entry['menu'].delete(0, 'end')

        # Add filtered options to the OptionMenu
        for type_option in filtered_types:
            self.item_type_entry['menu'].add_command(label=type_option,
                                                     command=tk._setit(self.type_value_inside, type_option))

        # Automatically set the first matching value, or reset if no match
        if filtered_types:
            self.type_value_inside.set(filtered_types[0])
        else:
            self.type_value_inside.set('Overig')

    def update_untappd(self):
        beer_url = self.check_barcode_existment_feedback_label.cget("text")
        self.untappd_getter.get_untappd(beer_url)
        self.feedback_label.config(text='Untappd geüpdated')
    def check_barcode_existment(self):
        barcode_value = self.check_barcode_existment_entry.get()
        found_product = self.existment_checker.check_existment(barcode_value)
        self.check_barcode_existment_feedback_label.config(text=found_product[1])
        if found_product:
            self.print_label_button['state'] = 'normal'
            self.update_untappd_button['state'] = 'normal'
        self.check_barcode_existment_entry.delete(0, 'end')

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


    def prepare_microcash_import(self):
        min_date = self.min_date_picker.get_date()
        min_time = self.min_time_picker.get()
        max_date = self.max_date_picker.get_date()
        max_time = self.max_time_picker.get()
        min_time_for_query = str(min_time) + ':00-00:00'
        max_time_for_query = str(max_time) + ':00-00:00'
        query = f'created_at_min={min_date} {min_time_for_query}&created_at_max={max_date} {max_time_for_query}'
        self.microcash_import_maker.prepare_import(query)
    def get_untappd(self):
        untappd_updated = self.untappd_getter.get_untappd('all')
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
