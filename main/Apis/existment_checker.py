import re

import requests
from bs4 import BeautifulSoup

from label_printer.label_printer import LabelPrinter


class ExistmentChecker:
    def check_existment(self, query):
        if 'https' not in query:
            self.shopify_store_url = f'https://7c70bf.myshopify.com/search?q={query}'
            response = requests.get(url=self.shopify_store_url)
            soup = BeautifulSoup(response.text, 'html.parser')
            try:
                number_of_results = int(re.findall(r'\d+', soup.find(id='ProductCountDesktop').string)[0])
            except AttributeError:
                number_of_results = 0
            if number_of_results == 0:
                return False, 'Geen resultaten gevonden'
            # if number_of_results > 1:
            #     return False, f'{number_of_results} resultaten gevonden, verfijn zoekopdracht'
            if number_of_results >= 1:
                print('open page')
                product_div = soup.find(class_='card__content')
                product_link = product_div.find_all('a', href=True)[0]['href']
                return True, product_link
                # self.get_information_for_label(product_link)
        elif 'https' in query:
            parts = query.split('/products')
            if len(parts) > 1:
                result = '/products' + parts[1]
            return True, result


    def print_label(self, product_link):
        product_title, product_price, untappd_score = self.get_information_for_label(product_link)
        self.label_printer = LabelPrinter()
        self.label_printer.print_label(product_title, product_price, untappd_score)


    def get_information_for_label(self, product_link):
        self.shopify_store_url = f'https://7c70bf.myshopify.com/{product_link}'
        response = requests.get(url=self.shopify_store_url)
        soup = BeautifulSoup(response.text, 'html.parser')
        product_title = soup.find(class_='product__title').find('h1').text
        product_info = soup.find(class_='product__description')
        product_price = soup.find(class_='price-item').text.strip()
        untappd_score = str(0)
        try:
            untappd_li = [li for li in product_info.find_all('li') if 'Untappd Score' in li.text]
            if untappd_li:
                # Extract the Untappd score
                untappd_score = untappd_li[0].text.split(':')[1].strip()
                print("Untappd Score:", untappd_score)
        except AttributeError:
            untappd_score = str(0)


        return product_title, product_price, untappd_score
