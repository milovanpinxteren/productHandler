import os
import re
import time

import requests
from dotenv import load_dotenv
from label_printer.print_label_selection import SelectionLabelPrinter
import pandas as pd

from microcash_importer.email_sender import EmailSender


class MicrocashProductMaker:
    def prepare_import(self, query):
        self.prepare_products(query)
        # beers_df = pd.DataFrame(columns=['ShopifyID', 'omschrijving', 'verkoopprijs', 'emballage', 'btw', 'inkoopprijs',
        #                                  'leverancier1', 'bestelnummer1', 'merk', 'groep', 'land', 'extra_barcode',
        #                                  'variant_koppelnr', 'voorraad', 'kratinhoud'
        #                                  ])
        all_beers = self.prepare_products(query)
        taken_barcodes = []
        beer_counter = 0
        rows = []
        for beer_selection in all_beers:  # each selection has 250 beers
            for beer in beer_selection:
                beer_counter += 1
                #         print(beer_counter)
                cleaned_emballage_text = re.sub(r'[^0-9.,]', '', beer['tags'])
                time.sleep(1)
                btw_groep = self.get_product_BTW_value(str(beer['id']))
                merk = self.get_product_brand(str(beer['id']))
                groep = self.get_product_type(str(beer['id']))
                time.sleep(0.2)
                barcode = beer['variants'][0]['barcode']
                variant_koppel_nr = ''
                kratinhoud = 0
                if barcode and len(barcode) > 3:
                    variant_koppel_nr = self.create_variant_koppel_nr(barcode)
                    kratinhoud = 1
                    if barcode not in taken_barcodes:
                        taken_barcodes.append(barcode)
                    elif barcode in taken_barcodes:
                        barcode = ''
                land = self.get_product_country(str(beer['id']))
                price_as_str = str(beer['variants'][0]['price']).replace('.', ',')
                emballage_as_str = str(cleaned_emballage_text).replace('.', ',')
                time.sleep(0.2)
                row = {'ShopifyID': str(beer['id']), 'omschrijving': beer['title'], 'verkoopprijs': price_as_str,
                       'emballage': emballage_as_str, 'btw': btw_groep, 'merk': merk, 'groep': groep, 'land': land,
                       'extra_barcode': barcode, 'variant_koppelnr': variant_koppel_nr, 'kratinhoud': kratinhoud,
                       'voorraad': beer['variants'][0]['inventory_quantity']
                       }
                rows.append(row)
                # beers_df = beers_df.append(row, ignore_index=True)
            beers_df = pd.DataFrame(rows)
            email_sender = EmailSender()
            email_sender.send_email(beers_df)
        # beers_df = pd.concat(rows, ignore_index=True)

        return rows
    def prepare_products(self, query):
        beerlist = SelectionLabelPrinter().get_beers_from_shopify(query)
        return beerlist

    def get_product_BTW_value(self, productID):
        load_dotenv()
        self.access_token = os.environ["ACCESS_TOKEN"]
        headers = {"Accept": "application/json", "Content-Type": "application/json",
                   "X-Shopify-Access-Token": self.access_token}
        shopify_store_url = f"https://7c70bf.myshopify.com/admin/api/2023-10/products/{productID}/metafields.json"

        try:
            response = requests.get(url=shopify_store_url, headers=headers)
            json_response = response.json()
            alcohol_percentage = None
            try:
                for metafield in json_response['metafields']:
                    if metafield['key'] == 'alcoholpercentage':
                        alcohol_percentage = metafield['value']
                if alcohol_percentage:
                    if float(alcohol_percentage) <= 0.5:
                        return 'L'  # 9% btw (BTW Laag)
                    elif float(alcohol_percentage) > 0.5:
                        return 'H'
                elif not alcohol_percentage:
                    return 'L'  # Als geen alcohol percentage meegegeven (glazen, eten)
            except KeyError:  # geen metafields gevonden
                return 'L'
        except Exception as e:
            print(e)
            return 'H'

    def get_product_brand(self, productID):
        load_dotenv()
        self.access_token = os.environ["ACCESS_TOKEN"]
        headers = {"Accept": "application/json", "Content-Type": "application/json",
                   "X-Shopify-Access-Token": self.access_token}
        shopify_store_url = f"https://7c70bf.myshopify.com/admin/api/2023-10/products/{productID}/metafields.json"
        try:
            response = requests.get(url=shopify_store_url, headers=headers)
            json_response = response.json()
            brand = None
            try:
                for metafield in json_response['metafields']:
                    if metafield['key'] == 'merk':
                        brand = metafield['value']
                if brand:
                    return brand[:5].upper()
                else:
                    return 'OVERI'
            except KeyError:
                return 'OVERI'
        except Exception as e:
            print(e)
            return 'OVERI'

    def get_product_type(self, productID):
        load_dotenv()
        self.access_token = os.environ["ACCESS_TOKEN"]
        headers = {"Accept": "application/json", "Content-Type": "application/json",
                   "X-Shopify-Access-Token": self.access_token}
        shopify_store_url = f"https://7c70bf.myshopify.com/admin/api/2023-10/products/{productID}/metafields.json"
        try:
            response = requests.get(url=shopify_store_url, headers=headers)
            json_response = response.json()
            brand = None
            try:
                for metafield in json_response['metafields']:
                    if metafield['key'] == 'soort_bier':
                        brand = metafield['value']
                if brand:
                    return brand[:5].upper()
                else:
                    return 'OVERI'
            except KeyError:
                return 'OVERI'
        except Exception as e:
            print(e)
            return 'OVERI'

    def get_product_country(self, productID):
        load_dotenv()
        self.access_token = os.environ["ACCESS_TOKEN"]
        headers = {"Accept": "application/json", "Content-Type": "application/json",
                   "X-Shopify-Access-Token": self.access_token}
        shopify_store_url = f"https://7c70bf.myshopify.com/admin/api/2023-10/products/{productID}/metafields.json"
        try:
            response = requests.get(url=shopify_store_url, headers=headers)
            json_response = response.json()
            brand = None
            try:
                for metafield in json_response['metafields']:
                    if metafield['key'] == 'land_van_herkomst':
                        brand = metafield['value']
                if brand:
                    return brand.upper()
                else:
                    return 'OVERIG'
            except KeyError:
                return 'OVERIG'
        except Exception as e:
            print(e)
            return 'OVERIG'

    def create_variant_koppel_nr(self, barcode):  # generates 7-digit hash-key starting with 1
        hashcode = hash(barcode)
        hashcode_str = str(hashcode).lstrip('-')  # Remove negative sign if present
        while len(hashcode_str) < 7:
            hashcode_str = '0' + hashcode_str  # Pad with zeros if necessary
        generated_number = '1' + hashcode_str[:6]
        return generated_number





