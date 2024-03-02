import os
import re

import requests
from bs4 import BeautifulSoup
from deep_translator import GoogleTranslator
from dotenv import load_dotenv


class UntappdGetter:
    # def __init__(self):
    def get_untappd(self, beers):
        self.found_beers = 0
        self.found_simpliefied = 0
        self.unfound_beers = 0
        self.no_href_found = 0
        self.errors = 0
        self.tried_beers = []
        self.unfound_beers_list = []
        if beers == 'all':
            all_beers = self.get_beers_from_shopify()
        else:
            all_beers = self.get_beer_from_shopify(beers)
        self.printed_labels = []
        for beer_selection in all_beers: #each selection has 250 beers
            for beer in beer_selection:
                try:
                    if 'Untappd' not in beer['body_html'] or len(all_beers) == 1:
                        title = beer['title']
                        if title.endswith('37.5 CL'):
                            title = title[:-10]
                        if title.endswith('CL') or title.endswith('1.5 L') and not title.endswith('37.5 CL'):
                            title = title[:-8]
                        elif title.endswith('(1 pint)'):
                            title = title[:-19]
                        elif title.endswith('1 L') or title.endswith('3 L') or title.endswith('5 L'):
                            title = title[:-4]
                        elif title.endswith('fust'):
                            title = title[:-11]
                        title = title.replace('zonder doos', '').replace('met doos', '')
                        info_to_add = self.get_beer_from_untappd(title)
                        if info_to_add:
                            self.update_shopify(beer['id'], beer['body_html'], info_to_add)
                    else:
                        print('Untappd already done')
                        self.printed_labels.append(beer['title'])
                except TypeError:
                    print('No body found for: ' + beer['title'])
                    self.unfound_beers_list.append(beer['title'])
        print('found beers: ', self.found_beers)
        print('unfound beers: ', self.unfound_beers)
        print('found simplified', self.found_simpliefied)
        print('no href found: ', self.no_href_found)
        print('errors: ', self.errors)
        print('unfound beer list: ', self.unfound_beers_list)
        print('printed labels: ', self.printed_labels)
        return 'done'
    def get_beers_from_shopify(self):
        # self.shopify_store_url = 'https://7c70bf.myshopify.com/admin/api/2023-10/products.json?limit=250'
        load_dotenv()
        self.access_token = os.environ["ACCESS_TOKEN"]
        self.headers = {"Accept": "application/json", "Content-Type": "application/json",
                   "X-Shopify-Access-Token": self.access_token}
        last_product_id = 0
        self.shopify_store_url = f"https://7c70bf.myshopify.com/admin/api/2023-10/products.json?since_id={last_product_id}"

        response = requests.get(url=self.shopify_store_url, headers=self.headers)
        status_code = response.status_code
        beer_list = []
        while status_code == 200:
            get_all_beers_url = f"https://7c70bf.myshopify.com/admin/api/2023-10/products.json?limit=250&since_id={last_product_id}"
            get_all_product_original_site_response = requests.get(url=get_all_beers_url, headers=self.headers)
            beer_list.append(get_all_product_original_site_response.json()['products'])
            status_code = get_all_product_original_site_response.status_code
            try:
                last_product_id = get_all_product_original_site_response.json()['products'][249]['id']
            except IndexError:
                status_code = 404
        return beer_list

    def get_beer_from_shopify(self, beer_url):
        # self.shopify_store_url = 'https://7c70bf.myshopify.com/admin/api/2023-10/products.json?limit=250'
        load_dotenv()
        self.access_token = os.environ["ACCESS_TOKEN"]
        print(beer_url)
        beer_list = []
        handle = beer_url.split('/')[-1].split('?')[0]
        self.headers = {"Accept": "application/json", "Content-Type": "application/json",
                   "X-Shopify-Access-Token": self.access_token}
        self.shopify_store_url = f"https://7c70bf.myshopify.com/admin/api/2023-10/products.json?handle={handle}"

        response = requests.get(url=self.shopify_store_url, headers=self.headers)
        if response.status_code == 200:
            beer_list.append(response.json()['products'])
        else:
            return beer_list == []

        return beer_list

    def get_beer_from_untappd(self, beer):
        beer_query = beer.replace(' ', '+')
        self.untappd_url = f'https://untappd.com/search?q={beer_query}'
        self.untappd_headers = {
            "Accept": "application/json", "Content-Type": "application/json",
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
        }
        response = requests.get(url=self.untappd_url, headers=self.untappd_headers)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            beer_items = soup.find_all('div', class_='beer-item')

            if len(beer_items) > 0:
                beer = beer_items[0]
                first_anchor = beer.find('a')
                # Extract the href attribute from the anchor tag
                if first_anchor:
                    href = first_anchor.get('href')
                    print(f"First href within beer-item: {beer_query}")
                    self.found_beers += 1
                    beer_url = 'https://untappd.com/' + href
                    info_to_add = self.get_beer_info_from_untappd(beer_url)
                    return info_to_add
                else:
                    print("No href found within beer-item", beer)
                    self.no_href_found += 1
                    return False
            elif len(beer_items) == 0:
                print('no beer on untappd found for ', beer_query)
                found_simplified_name = self.simplify_beer_name(beer)
                if found_simplified_name:
                    self.found_simpliefied += 1
                    return found_simplified_name
                else:
                    self.unfound_beers += 1
                    self.unfound_beers_list.append(beer)
                    return False
        else:
            print("Error fetching beer information from Untappd:", response.status_code)
            self.errors += 1
            return False

    def get_beer_info_from_untappd(self, beer_url):
        response = requests.get(url=beer_url, headers=self.untappd_headers)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            caps_div = soup.find('div', class_='caps') #div with the untappd score (including image)
            untappd_score = caps_div.get('data-rating') #score as string
            description = soup.find('div', class_='beer-descrption-read-less').text
            description = description.replace('Show More', '').replace('Show Less', '')
            translated_description = GoogleTranslator(soruce='auto', target='nl').translate(description)
            translated_description = translated_description.replace(' we ', ' de brouwers ').replace(' wij ', ' de brouwers ').replace(' wij ', ' de brouwers ')
            return [caps_div, untappd_score, translated_description]

        else:
            print("Error fetching beer information from Untappd:", response.status_code)
            self.errors += 1

    def update_shopify(self, productID, original_body, info_to_add):
        # print('update', original_body, info_to_add)
        soup = BeautifulSoup(original_body, 'html.parser')
        li_with_volume = [li for li in soup.find_all('li') if 'Volume' in li.text]
        li_with_percentage = [li for li in soup.find_all('li') if 'Alcoholpercentage' in li.text]

        rating_stars = info_to_add[0]
        ratings = rating_stars.find_all('div', class_='cap')
        for rating in ratings:
            try:
                class_name = rating['class'][1]
            except IndexError:
                class_name = 'cap'
            img_tag = soup.new_tag('img', src=f'https://untappd.com/assets/images/ratings/{class_name}@2x.png')
            img_tag["style"] = "max-height: 25px;"
            rating.append(img_tag)

        rating_stars["style"] = "display: flex;"
        try:
            new_html = f"""
            <p>
            {info_to_add[2]}
            </p><br>
            <h3>Productdetails:</h3>
            <ul>
            {li_with_percentage[0]}
            {li_with_volume[0]}
            <li>Untappd Score: {info_to_add[1][:4]} {rating_stars}</li>
            </ul>
            """
        except IndexError:
            new_html = ''
        update_product_url = f"https://7c70bf.myshopify.com/admin/api/2023-10/products/{productID}.json"
        payload = {"product": {
            "id": productID,
            "body_html": new_html,
        }}
        response = requests.put(update_product_url, headers=self.headers, json=payload)
        print(response)

    def simplify_beer_name(self, beer):

        if beer not in self.tried_beers and len(beer) > 1:
            if beer.endswith(' '):
                new_beer = beer[:-1]
            elif bool(re.search(r'\d{4}$', beer)): #if beer ends in year
                new_beer = beer[:-5]
            else:  #remove the last word
                new_beer = ' '.join(beer.split()[:-1])



            found_beer = self.get_beer_from_untappd(new_beer)
            self.tried_beers.append(beer)
            return found_beer
        elif beer in self.tried_beers:
            return False

# untappd_getter = UntappdGetter()