import os

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

from label_printer.label_printer import LabelPrinter


class SelectionLabelPrinter:
    def get_beers_from_shopify(self, query):
        load_dotenv()
        self.access_token = os.environ["ACCESS_TOKEN"]
        self.headers = {"Accept": "application/json", "Content-Type": "application/json",
                        "X-Shopify-Access-Token": self.access_token}
        self.shopify_store_url = f"https://7c70bf.myshopify.com/admin/api/2023-10/products.json?{query}&limit=250"

        response = requests.get(url=self.shopify_store_url, headers=self.headers)
        status_code = response.status_code
        beer_list = []
        if status_code == 200:
            beer_list.append(response.json()['products'])
        return beer_list

    def print_labels(self, query):
        label_printer = LabelPrinter()
        all_beers = self.get_beers_from_shopify(query)
        for beer_selection in all_beers:  # each selection has 250 beers
            for beer in beer_selection:
                product_title, product_price, untappd_score = self.send_text_to_printer(
                    'products/' + beer['handle'])
                label_printer.print_label(product_title, product_price, untappd_score)

    def send_text_to_printer(self, product_link):
        self.shopify_store_url = f'https://7c70bf.myshopify.com/{product_link}'
        response = requests.get(url=self.shopify_store_url)
        soup = BeautifulSoup(response.text, 'html.parser')
        product_title = soup.find(class_='product__title').find('h1').text
        product_info = soup.find(class_='product__description')
        product_price = soup.find(class_='price-item').text.strip()
        try:
            untappd_li = [li for li in product_info.find_all('li') if 'Untappd Score' in li.text]
            untappd_score = ''
            if untappd_li:
                # Extract the Untappd score
                untappd_score = untappd_li[0].text.split(':')[1].strip()
                print("Untappd Score:", untappd_score)

            return product_title, product_price, untappd_score
        except AttributeError:
            return product_title, product_price, ''